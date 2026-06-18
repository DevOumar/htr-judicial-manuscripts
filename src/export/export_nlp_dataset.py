"""Build the final NLP-ready transcription dataset from judicial outputs."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import unicodedata
from pathlib import Path
from typing import Any, Dict, List

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from PIL import Image

from src.segmentation.kraken_segmentation import write_page_xml


def collect_page_outputs(input_dir: str = "outputs/judicial_demo") -> List[Path]:
    """Collect page output directories from the judicial demo.

    Args:
        input_dir: Directory containing `page_*_canvas_*` folders.

    Returns:
        Sorted page directories containing a `transcriptions.json` file.
    """
    return [
        path
        for path in sorted(Path(input_dir).glob("page_*_canvas_*"))
        if (path / "transcriptions.json").exists()
    ]


def _load_demo_report(input_dir: str) -> Dict[str, Any]:
    report_path = Path(input_dir) / "demo_report.json"
    if not report_path.exists():
        return {}
    return json.load(report_path.open("r", encoding="utf-8"))


def _load_lines(page_dir: Path, htr_source: str, kraken_dir: str) -> List[Dict[str, Any]]:
    if htr_source == "kraken":
        path = Path(kraken_dir) / page_dir.name / "transcriptions_kraken.json"
        if path.exists():
            return json.load(path.open("r", encoding="utf-8"))
    return json.load((page_dir / "transcriptions.json").open("r", encoding="utf-8"))


def _load_regions(page_dir: Path) -> List[Dict[str, Any]]:
    polygons_path = page_dir / "polygons.json"
    if not polygons_path.exists():
        return []
    return json.load(polygons_path.open("r", encoding="utf-8")).get("regions", [])


def _write_htr_page_xml(page_dir: Path, page_xml_path: Path, lines: List[Dict[str, Any]]) -> None:
    image_path = page_dir / "segmentation_input.png"
    with Image.open(image_path) as image:
        image_size = image.size
    write_page_xml(
        output_path=page_xml_path,
        image_filename=image_path.name,
        image_size=image_size,
        regions=_load_regions(page_dir),
        lines=lines,
    )


def build_dataset(
    input_dir: str = "outputs/judicial_demo",
    output_dir: str = "dataset_nlp",
    segmentations_dir: str = "segmentations",
    htr_source: str = "trocr",
    kraken_dir: str = "outputs/kraken_ocr_judicial",
) -> Dict[str, Any]:
    """Create the final JSON dataset and reusable segmentation exports.

    Args:
        input_dir: Judicial pipeline output directory.
        output_dir: Destination for NLP-ready JSON files.
        segmentations_dir: Destination for PAGE XML and polygon files.
        htr_source: `trocr` for original pipeline text or `kraken` for the
            improved Kraken recognition outputs.
        kraken_dir: Directory containing `transcriptions_kraken.json` files.

    Returns:
        Metadata summary for the generated dataset.

    Raises:
        FileNotFoundError: If no page-level transcription outputs are found.
    """
    page_dirs = collect_page_outputs(input_dir)
    if not page_dirs:
        raise FileNotFoundError(f"No page transcriptions found in {input_dir}")

    output = Path(output_dir)
    page_xml_output = Path(segmentations_dir) / "page_xml"
    polygons_output = Path(segmentations_dir) / "polygons"
    output.mkdir(parents=True, exist_ok=True)
    page_xml_output.mkdir(parents=True, exist_ok=True)
    polygons_output.mkdir(parents=True, exist_ok=True)

    demo_report = _load_demo_report(input_dir)
    rows: List[Dict[str, Any]] = []
    pages: List[Dict[str, Any]] = []

    for page_dir in page_dirs:
        page_id = page_dir.name
        lines = _load_lines(page_dir, htr_source, kraken_dir)
        page_xml_path = page_dir / "page.xml"
        polygons_path = page_dir / "polygons.json"
        copied_xml = page_xml_output / f"{page_id}.xml"
        copied_polygons = polygons_output / f"{page_id}_polygons.json"

        if htr_source != "kraken" and page_xml_path.exists():
            shutil.copy2(page_xml_path, copied_xml)
        if polygons_path.exists():
            shutil.copy2(polygons_path, copied_polygons)

        page_rows = []
        for line in sorted(lines, key=lambda item: item.get("order", 0)):
            record = dict(line)
            record["page_id"] = record.get("page_id") or page_id
            record["image_id"] = record.get("image_id") or page_id
            record["line_id"] = record.get("line_id") or record.get("id")
            record["transcription"] = unicodedata.normalize("NFC", record.get("transcription") or record.get("prediction", ""))
            if not record["transcription"].strip():
                record["transcription"] = "[UNK]"
                record["needs_review"] = True
                record["confidence"] = 0.0
            record["prediction"] = record["transcription"]
            record["confidence"] = float(record.get("confidence", 0.0))
            record["needs_review"] = bool(record.get("needs_review", True))
            record["source_image"] = record.get("source_image") or str(page_dir / "segmentation_input.png")
            record["model_name"] = record.get("model_name") or "models/trocr-catmus-french-decoder/final"
            record["page_xml"] = str(copied_xml)
            record["polygons_file"] = str(copied_polygons)
            page_rows.append(record)
            rows.append(record)

        page_json_path = output / f"{page_id}.json"
        if htr_source == "kraken":
            _write_htr_page_xml(page_dir, copied_xml, page_rows)
        with page_json_path.open("w", encoding="utf-8") as handle:
            json.dump(page_rows, handle, indent=2, ensure_ascii=False)
        full_page_path = output / f"{page_id}_full_page_transcription.txt"
        full_page_path.write_text(
            "\n".join(row["transcription"] for row in sorted(page_rows, key=lambda item: item.get("order", 0))),
            encoding="utf-8",
        )

        pages.append(
            {
                "page_id": page_id,
                "num_lines": len(page_rows),
                "json": str(page_json_path),
                "page_xml": str(copied_xml),
                "polygons": str(copied_polygons),
                "full_page_transcription": str(full_page_path),
            }
        )

    dataset_path = output / "transcriptions.json"
    with dataset_path.open("w", encoding="utf-8") as handle:
        json.dump(rows, handle, indent=2, ensure_ascii=False)

    metadata = {
        "name": "Parlement de Paris judicial HTR dataset",
        "source_pipeline": input_dir,
        "num_pages": len(pages),
        "num_lines": len(rows),
        "corpus": demo_report.get("corpus", {}),
        "schema": "schemas/transcription_schema.json",
        "htr_source": htr_source,
        "kraken_dir": kraken_dir if htr_source == "kraken" else None,
        "pages": pages,
        "quality_note": (
            "All lines are machine-generated HTR predictions. Lines marked "
            "needs_review=true should be manually corrected before NLP use."
        ),
    }
    with (output / "metadata.json").open("w", encoding="utf-8") as handle:
        json.dump(metadata, handle, indent=2, ensure_ascii=False)
    (output / "README.md").write_text(
        "# NLP Transcription Dataset\n\n"
        "This directory contains the JSON dataset required by the MD5 brief.\n\n"
        "- `transcriptions.json`: flat line-level dataset validated by `schemas/transcription_schema.json`.\n"
        "- `page_*.json`: page-level line datasets.\n"
        "- `metadata.json`: corpus, source and file metadata.\n\n"
        f"HTR source: `{htr_source}`.\n\n"
        "Important: the current text is machine-generated HTR and must be reviewed for scholarly use. "
        "Use `needs_review` and `confidence` to prioritize manual correction. "
        "Empty raw predictions are exported as `[UNK]` so that PAGE XML and JSON remain structurally valid.\n",
        encoding="utf-8",
    )

    print(json.dumps(metadata, indent=2, ensure_ascii=False))
    return metadata


def main() -> None:
    """Run final NLP dataset export."""
    parser = argparse.ArgumentParser(description="Export final NLP-ready judicial transcription dataset.")
    parser.add_argument("--input-dir", default="outputs/judicial_demo")
    parser.add_argument("--output-dir", default="dataset_nlp")
    parser.add_argument("--segmentations-dir", default="segmentations")
    parser.add_argument("--htr-source", choices=["trocr", "kraken"], default="trocr")
    parser.add_argument("--kraken-dir", default="outputs/kraken_ocr_judicial")
    args = parser.parse_args()
    build_dataset(args.input_dir, args.output_dir, args.segmentations_dir, args.htr_source, args.kraken_dir)


if __name__ == "__main__":
    main()
