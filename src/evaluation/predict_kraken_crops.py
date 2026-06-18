"""Predict judicial line crops with a Kraken recognition model."""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from pathlib import Path
from statistics import mean
from typing import Any, Dict, List

from PIL import Image
from kraken.containers import BaselineLine, Segmentation
from kraken.lib import models
from kraken.rpred import rpred

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.evaluation.quality_flags import enrich_line_quality


DEFAULT_MODEL = (
    r"C:\Users\33767\AppData\Local\htrmopo\htrmopo"
    r"\34468dee-e4d7-5607-88d3-74a357bf60e8\ManuMcFrenchV3.mlmodel"
)


def _whole_line_segmentation(image_path: Path, image: Image.Image) -> Segmentation:
    """Create a one-line baseline segmentation for a line crop."""
    width, height = image.size
    if width < 8 or height < 8:
        baseline_y = max(0, height // 2)
        boundary = [(0, 0), (max(0, width - 1), 0), (max(0, width - 1), max(0, height - 1)), (0, max(0, height - 1))]
        baseline = [(0, baseline_y), (max(0, width - 1), baseline_y)]
    else:
        baseline_y = min(height - 2, max(2, int(height * 0.72)))
        boundary = [(1, 1), (width - 2, 1), (width - 2, height - 2), (1, height - 2)]
        baseline = [(1, baseline_y), (width - 2, baseline_y)]
    line = BaselineLine(
        id=image_path.stem,
        baseline=baseline,
        boundary=boundary,
    )
    return Segmentation(
        type="baselines",
        imagename=str(image_path),
        text_direction="horizontal-lr",
        script_detection=False,
        lines=[line],
    )


def predict_crop(network: Any, crop_path: Path) -> Dict[str, Any]:
    """Predict one crop with an already loaded Kraken model."""
    start = time.perf_counter()
    image = Image.open(crop_path).convert("RGB")
    segmentation = _whole_line_segmentation(crop_path, image)
    records = list(rpred(network, image, segmentation, pad=16, bidi_reordering=False))
    prediction = records[0].prediction if records else ""
    confidences = list(records[0].confidences) if records and records[0].confidences is not None else []
    confidence = float(mean(confidences)) if confidences else 0.0
    return {
        "crop_path": str(crop_path),
        "prediction": prediction,
        "confidence": confidence,
        "seconds": time.perf_counter() - start,
    }


def _load_page_lines(page_dir: Path) -> List[Dict[str, Any]]:
    return json.load((page_dir / "transcriptions.json").open("r", encoding="utf-8"))


def predict_judicial_crops(
    input_dir: str = "outputs/judicial_demo",
    output_dir: str = "outputs/kraken_ocr_judicial",
    model_path: str = DEFAULT_MODEL,
) -> Dict[str, Any]:
    """Run Kraken recognition on all judicial line crops.

    Args:
        input_dir: Existing judicial pipeline output directory.
        output_dir: Destination for Kraken predictions.
        model_path: Kraken `.mlmodel` recognition model.

    Returns:
        Summary report with paths and runtime metrics.
    """
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    network = models.load_any(model_path, device="cpu")

    all_rows: List[Dict[str, Any]] = []
    page_reports = []
    total_start = time.perf_counter()
    for page_dir in sorted(Path(input_dir).glob("page_*_canvas_*")):
        if not (page_dir / "transcriptions.json").exists():
            continue
        page_id = page_dir.name
        page_output = output / page_id
        page_output.mkdir(parents=True, exist_ok=True)
        page_lines = _load_page_lines(page_dir)
        page_rows = []
        for line in sorted(page_lines, key=lambda item: item.get("order", 0)):
            crop_path = Path(line.get("crop_path", ""))
            if not crop_path.exists():
                continue
            pred = predict_crop(network, crop_path)
            row = {
                **line,
                "page_id": page_id,
                "image_id": line.get("image_id") or page_id,
                "line_id": line.get("line_id") or line.get("id"),
                "trocr_prediction": line.get("prediction", ""),
                "prediction": pred["prediction"],
                "transcription": pred["prediction"],
                "confidence": pred["confidence"],
                "transcription_seconds": pred["seconds"],
                "model_name": model_path,
                "htr_engine": "kraken",
            }
            row = enrich_line_quality(row, model_path)
            page_rows.append(row)
            all_rows.append(row)

        with (page_output / "transcriptions_kraken.json").open("w", encoding="utf-8") as handle:
            json.dump(page_rows, handle, indent=2, ensure_ascii=False)
        (page_output / "full_page_transcription_kraken.txt").write_text(
            "\n".join(row["prediction"] for row in page_rows),
            encoding="utf-8",
        )
        page_reports.append(
            {
                "page_id": page_id,
                "num_lines": len(page_rows),
                "json": str(page_output / "transcriptions_kraken.json"),
                "full_page_transcription": str(page_output / "full_page_transcription_kraken.txt"),
            }
        )

    with (output / "kraken_predictions.json").open("w", encoding="utf-8") as handle:
        json.dump(all_rows, handle, indent=2, ensure_ascii=False)
    with (output / "kraken_predictions.csv").open("w", encoding="utf-8", newline="") as handle:
        fieldnames = [
            "page_id",
            "line_id",
            "order",
            "crop_path",
            "trocr_prediction",
            "prediction",
            "confidence",
            "needs_review",
            "transcription_seconds",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(all_rows)

    total_seconds = time.perf_counter() - total_start
    report = {
        "input_dir": input_dir,
        "output_dir": output_dir,
        "model_path": model_path,
        "num_pages": len(page_reports),
        "num_lines": len(all_rows),
        "total_seconds": total_seconds,
        "average_seconds_per_line": total_seconds / len(all_rows) if all_rows else 0.0,
        "pages": page_reports,
    }
    with (output / "kraken_ocr_report.json").open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, ensure_ascii=False)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return report


def main() -> None:
    """Run Kraken OCR on judicial crops."""
    parser = argparse.ArgumentParser(description="Predict judicial line crops with a Kraken recognition model.")
    parser.add_argument("--input-dir", default="outputs/judicial_demo")
    parser.add_argument("--output-dir", default="outputs/kraken_ocr_judicial")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    args = parser.parse_args()
    predict_judicial_crops(args.input_dir, args.output_dir, args.model)


if __name__ == "__main__":
    main()
