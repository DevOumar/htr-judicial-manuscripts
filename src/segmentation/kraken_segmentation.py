import argparse
import json
import shutil
import sys
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

import torch
from datasets import load_dataset
from kraken import blla
from lxml import etree
from PIL import Image, ImageDraw
from transformers import TrOCRProcessor, VisionEncoderDecoderModel

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.utils.config import load_config
from src.evaluation.quality_flags import enrich_line_quality


Point = Tuple[int, int]


def _ensure_dir(path: str | Path) -> Path:
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def _clean_generated_outputs(output_dir: Path) -> None:
    for filename in [
        "original.png",
        "segmentation_input.png",
        "annotated.png",
        "polygons.json",
        "ground_truth_objects.json",
        "page.xml",
        "transcriptions.json",
        "full_page_transcription.txt",
        "segmentation_report.json",
    ]:
        path = output_dir / filename
        if path.exists():
            path.unlink()

    lines_dir = output_dir / "lines"
    if lines_dir.exists():
        shutil.rmtree(lines_dir)


def _resize_for_segmentation(image: Image.Image, max_side: int | None) -> Image.Image:
    if not max_side or max(image.size) <= max_side:
        return image.convert("RGB")

    width, height = image.size
    scale = max_side / max(width, height)
    new_size = (max(1, int(width * scale)), max(1, int(height * scale)))
    return image.convert("RGB").resize(new_size, Image.Resampling.LANCZOS)


def _points_to_list(points: Iterable[Point] | None) -> List[List[int]]:
    if not points:
        return []
    return [[int(x), int(y)] for x, y in points]


def _flat_points(points: Iterable[Point] | None) -> str:
    return " ".join(f"{int(x)},{int(y)}" for x, y in (points or []))


def _bbox_from_polygon(points: List[Point], image_size: Tuple[int, int]) -> Tuple[int, int, int, int]:
    width, height = image_size
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    left = max(min(xs), 0)
    top = max(min(ys), 0)
    right = min(max(xs), width)
    bottom = min(max(ys), height)
    return int(left), int(top), int(right), int(bottom)


def load_page_from_huggingface(dataset_name: str, split: str, sample_index: int) -> Dict[str, Any]:
    stream = load_dataset(dataset_name, split=split, streaming=True)
    for index, row in enumerate(stream):
        if index == sample_index:
            return row
    raise IndexError(f"Sample index {sample_index} not found in split '{split}'.")


def load_page(config: Dict[str, Any], image_path: str | None = None) -> Dict[str, Any]:
    if image_path:
        image = Image.open(image_path).convert("RGB")
        return {
            "image": image,
            "source": str(image_path),
            "shelfmark": Path(image_path).stem,
            "objects": None,
        }

    segmentation_config = config.get("segmentation", {})
    row = load_page_from_huggingface(
        segmentation_config.get("dataset_name", "CATMuS/medieval-segmentation"),
        segmentation_config.get("split", "test"),
        int(segmentation_config.get("sample_index", 0)),
    )
    row["image"] = row["image"].convert("RGB")
    row["source"] = segmentation_config.get("dataset_name", "CATMuS/medieval-segmentation")
    return row


def run_kraken(image: Image.Image, text_direction: str = "horizontal-lr", device: str = "cpu"):
    return blla.segment(image, text_direction=text_direction, device=device)


def serialize_regions(segmentation: Any) -> List[Dict[str, Any]]:
    regions = []
    raw_regions = getattr(segmentation, "regions", None) or {}
    if isinstance(raw_regions, dict):
        items = []
        for category, values in raw_regions.items():
            for value in values:
                items.append((category, value))
    else:
        items = [("region", value) for value in raw_regions]

    for index, (category, region) in enumerate(items):
        regions.append(
            {
                "id": getattr(region, "id", f"region_{index:04d}"),
                "category": category,
                "polygon": _points_to_list(getattr(region, "boundary", [])),
            }
        )
    return regions


def serialize_lines(segmentation: Any) -> List[Dict[str, Any]]:
    lines = []
    for index, line in enumerate(getattr(segmentation, "lines", []) or []):
        line_id = getattr(line, "id", None) or f"line_{index:04d}"
        lines.append(
            {
                "id": line_id,
                "order": index,
                "baseline": _points_to_list(getattr(line, "baseline", [])),
                "polygon": _points_to_list(getattr(line, "boundary", [])),
                "regions": list(getattr(line, "regions", []) or []),
                "text": getattr(line, "text", None),
            }
        )
    return lines


def save_line_crops(image: Image.Image, lines: List[Dict[str, Any]], output_dir: Path) -> List[Dict[str, Any]]:
    lines_dir = _ensure_dir(output_dir / "lines")
    enriched = []
    for line in lines:
        polygon = [tuple(point) for point in line["polygon"]]
        if len(polygon) < 3:
            continue
        bbox = _bbox_from_polygon(polygon, image.size)
        if bbox[2] <= bbox[0] or bbox[3] <= bbox[1]:
            continue
        crop = image.crop(bbox)
        crop_path = lines_dir / f"{line['order']:04d}_{line['id']}.png"
        crop.save(crop_path)
        enriched_line = dict(line)
        enriched_line["bbox"] = list(bbox)
        enriched_line["crop_path"] = str(crop_path)
        enriched.append(enriched_line)
    return enriched


def save_annotated_image(image: Image.Image, regions: List[Dict[str, Any]], lines: List[Dict[str, Any]], output_path: Path) -> None:
    annotated = image.copy()
    draw = ImageDraw.Draw(annotated, "RGBA")

    for region in regions:
        polygon = [tuple(point) for point in region["polygon"]]
        if len(polygon) >= 3:
            draw.polygon(polygon, outline=(0, 128, 255, 255), fill=(0, 128, 255, 35))

    for line in lines:
        polygon = [tuple(point) for point in line["polygon"]]
        baseline = [tuple(point) for point in line["baseline"]]
        if len(polygon) >= 3:
            draw.line(polygon + [polygon[0]], fill=(255, 0, 0, 255), width=2)
        if len(baseline) >= 2:
            draw.line(baseline, fill=(0, 200, 0, 255), width=2)
        if polygon:
            draw.text(polygon[0], str(line["order"]), fill=(255, 255, 0, 255))

    annotated.save(output_path)


def save_polygons_json(
    output_path: Path,
    source: Dict[str, Any],
    regions: List[Dict[str, Any]],
    lines: List[Dict[str, Any]],
) -> None:
    payload = {
        "source": {
            "dataset_or_file": source.get("source"),
            "shelfmark": source.get("shelfmark"),
            "century": source.get("century"),
            "project": source.get("project"),
        },
        "regions": regions,
        "lines": lines,
    }
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)


def save_ground_truth_json(output_path: Path, source: Dict[str, Any]) -> None:
    objects = source.get("objects")
    if not objects:
        return

    rows = []
    for index, object_id in enumerate(objects.get("id", [])):
        rows.append({key: values[index] for key, values in objects.items()})

    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(rows, handle, indent=2, ensure_ascii=False)


def write_page_xml(
    output_path: Path,
    image_filename: str,
    image_size: Tuple[int, int],
    regions: List[Dict[str, Any]],
    lines: List[Dict[str, Any]],
) -> None:
    namespace = "http://schema.primaresearch.org/PAGE/gts/pagecontent/2019-07-15"
    nsmap = {None: namespace}
    root = etree.Element(f"{{{namespace}}}PcGts", nsmap=nsmap)
    metadata = etree.SubElement(root, f"{{{namespace}}}Metadata")
    etree.SubElement(metadata, f"{{{namespace}}}Creator").text = "htr-judicial-manuscripts Kraken pipeline"

    page = etree.SubElement(
        root,
        f"{{{namespace}}}Page",
        imageFilename=image_filename,
        imageWidth=str(image_size[0]),
        imageHeight=str(image_size[1]),
    )

    if not regions:
        regions = [
            {
                "id": "region_full_page",
                "category": "FullPage",
                "polygon": [[0, 0], [image_size[0], 0], [image_size[0], image_size[1]], [0, image_size[1]]],
            }
        ]

    region_by_id = {region["id"]: region for region in regions}
    lines_by_region: Dict[str, List[Dict[str, Any]]] = {region["id"]: [] for region in regions}
    unassigned_lines = []

    for line in lines:
        assigned = False
        for region_id in line.get("regions", []):
            if region_id in lines_by_region:
                lines_by_region[region_id].append(line)
                assigned = True
        if not assigned:
            unassigned_lines.append(line)

    if unassigned_lines:
        full_page_region = {
            "id": "region_unassigned_lines",
            "category": "Text",
            "polygon": [[0, 0], [image_size[0], 0], [image_size[0], image_size[1]], [0, image_size[1]]],
        }
        region_by_id[full_page_region["id"]] = full_page_region
        lines_by_region[full_page_region["id"]] = unassigned_lines

    for region_id, region_lines in lines_by_region.items():
        region = region_by_id[region_id]
        text_region = etree.SubElement(page, f"{{{namespace}}}TextRegion", id=region["id"], type=region.get("category", "Text"))
        etree.SubElement(text_region, f"{{{namespace}}}Coords", points=_flat_points([tuple(point) for point in region["polygon"]]))

        for line in region_lines:
            text_line = etree.SubElement(text_region, f"{{{namespace}}}TextLine", id=line["id"])
            etree.SubElement(text_line, f"{{{namespace}}}Coords", points=_flat_points([tuple(point) for point in line["polygon"]]))
            if line.get("baseline"):
                etree.SubElement(text_line, f"{{{namespace}}}Baseline", points=_flat_points([tuple(point) for point in line["baseline"]]))
            if line.get("prediction"):
                attributes = {}
                if line.get("confidence") is not None:
                    attributes["conf"] = f"{float(line['confidence']):.4f}"
                text_equiv = etree.SubElement(text_line, f"{{{namespace}}}TextEquiv", **attributes)
                etree.SubElement(text_equiv, f"{{{namespace}}}Unicode").text = line["prediction"]

    etree.ElementTree(root).write(str(output_path), pretty_print=True, xml_declaration=True, encoding="utf-8")


def transcribe_lines(
    lines: List[Dict[str, Any]],
    model_path: str,
    max_lines: int | None,
    max_length: int,
    num_beams: int,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    start_time = time.perf_counter()
    if not lines:
        return lines, {
            "total_lines": 0,
            "transcribed_lines": 0,
            "total_seconds": 0.0,
            "average_seconds_per_line": 0.0,
        }

    processor = TrOCRProcessor.from_pretrained(model_path)
    model = VisionEncoderDecoderModel.from_pretrained(model_path)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()

    enriched = []
    transcribed_count = 0
    for index, line in enumerate(lines):
        output_line = dict(line)
        should_transcribe = max_lines is None or index < max_lines
        if should_transcribe and line.get("crop_path"):
            line_start = time.perf_counter()
            image = Image.open(line["crop_path"]).convert("RGB")
            pixel_values = processor(images=image, return_tensors="pt").pixel_values.to(device)
            with torch.no_grad():
                generated = model.generate(
                    pixel_values,
                    max_length=max_length,
                    num_beams=num_beams,
                    output_scores=True,
                    return_dict_in_generate=True,
                )
            generated_ids = generated.sequences
            output_line["prediction"] = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            if generated.scores:
                token_confidences = [torch.softmax(score, dim=-1).max().item() for score in generated.scores]
                output_line["confidence"] = float(sum(token_confidences) / len(token_confidences))
            output_line["transcription_seconds"] = time.perf_counter() - line_start
            transcribed_count += 1
        output_line = enrich_line_quality(output_line, model_path)
        enriched.append(output_line)

    total_seconds = time.perf_counter() - start_time
    metrics = {
        "total_lines": len(lines),
        "transcribed_lines": transcribed_count,
        "total_seconds": total_seconds,
        "average_seconds_per_line": total_seconds / transcribed_count if transcribed_count else 0.0,
    }
    return enriched, metrics


def write_full_page_transcription(output_path: Path, lines: List[Dict[str, Any]]) -> None:
    ordered_lines = sorted(lines, key=lambda line: line.get("order", 0))
    text = "\n".join(line.get("prediction", "") for line in ordered_lines)
    output_path.write_text(text, encoding="utf-8")


def write_segmentation_report(output_path: Path, summary: Dict[str, Any]) -> None:
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, ensure_ascii=False)


def segment_page(config_path: str = "config.yaml", image_path: str | None = None, transcribe: bool | None = None) -> Dict[str, Any]:
    config = load_config(config_path)
    segmentation_config = config.get("segmentation", {})
    output_dir = _ensure_dir(segmentation_config.get("output_dir", "outputs/segmentation"))
    return segment_page_with_config(config, output_dir, image_path, transcribe)


def segment_page_with_config(
    config: Dict[str, Any],
    output_dir: str | Path,
    image_path: str | None = None,
    transcribe: bool | None = None,
    max_transcribed_lines: int | None = None,
) -> Dict[str, Any]:
    segmentation_config = config.get("segmentation", {})
    output_dir = _ensure_dir(output_dir)
    _clean_generated_outputs(output_dir)

    page = load_page(config, image_path)
    original = page["image"].convert("RGB")
    segment_image = _resize_for_segmentation(original, segmentation_config.get("max_page_side", 1800))

    original_path = output_dir / "original.png"
    segment_path = output_dir / "segmentation_input.png"
    annotated_path = output_dir / "annotated.png"
    polygons_path = output_dir / "polygons.json"
    ground_truth_path = output_dir / "ground_truth_objects.json"
    page_xml_path = output_dir / "page.xml"
    transcriptions_path = output_dir / "transcriptions.json"
    full_transcription_path = output_dir / "full_page_transcription.txt"
    report_path = output_dir / "segmentation_report.json"

    original.save(original_path)
    segment_image.save(segment_path)

    segmentation = run_kraken(
        segment_image,
        text_direction=segmentation_config.get("text_direction", "horizontal-lr"),
        device=segmentation_config.get("device", "cpu"),
    )
    regions = serialize_regions(segmentation)
    lines = serialize_lines(segmentation)
    lines = save_line_crops(segment_image, lines, output_dir)
    for line in lines:
        line["image_id"] = Path(image_path).stem if image_path else str(page.get("shelfmark") or output_dir.name)
        line["page_id"] = output_dir.name
        line["line_id"] = line.get("id")
        line["source_image"] = str(segment_path)
        line["model_name"] = str(Path(config["model"]["output_dir"]) / "final")

    should_transcribe = segmentation_config.get("transcribe", True) if transcribe is None else transcribe
    transcription_metrics = {
        "total_lines": len(lines),
        "transcribed_lines": 0,
        "total_seconds": 0.0,
        "average_seconds_per_line": 0.0,
    }
    if should_transcribe:
        configured_max_lines = segmentation_config.get("max_transcribed_lines")
        effective_max_lines = max_transcribed_lines if max_transcribed_lines is not None else configured_max_lines
        lines, transcription_metrics = transcribe_lines(
            lines,
            model_path=str(Path(config["model"]["output_dir"]) / "final"),
            max_lines=int(effective_max_lines) if effective_max_lines is not None else None,
            max_length=int(config.get("training", {}).get("generation_max_length", 64)),
            num_beams=int(config.get("training", {}).get("generation_num_beams", 1)),
        )

    save_annotated_image(segment_image, regions, lines, annotated_path)
    save_polygons_json(polygons_path, page, regions, lines)
    save_ground_truth_json(ground_truth_path, page)
    write_page_xml(page_xml_path, segment_path.name, segment_image.size, regions, lines)
    write_full_page_transcription(full_transcription_path, lines)

    with transcriptions_path.open("w", encoding="utf-8") as handle:
        json.dump(lines, handle, indent=2, ensure_ascii=False)

    summary = {
        "output_dir": str(output_dir),
        "original": str(original_path),
        "segmentation_input": str(segment_path),
        "annotated": str(annotated_path),
        "polygons": str(polygons_path),
        "page_xml": str(page_xml_path),
        "transcriptions": str(transcriptions_path),
        "full_page_transcription": str(full_transcription_path),
        "report": str(report_path),
        "num_regions": len(regions),
        "num_lines": len(lines),
        "num_transcribed_lines": len([line for line in lines if line.get("prediction")]),
        "transcription": transcription_metrics,
    }
    write_segmentation_report(report_path, summary)
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Segment a full manuscript page with Kraken and optionally transcribe lines with TrOCR.")
    parser.add_argument("--config", default="config.yaml")
    parser.add_argument("--image", default=None, help="Optional local page image. If omitted, CATMuS segmentation is used.")
    parser.add_argument("--no-transcribe", action="store_true", help="Run segmentation only.")
    args = parser.parse_args()
    segment_page(args.config, args.image, transcribe=not args.no_transcribe)


if __name__ == "__main__":
    main()
