"""Geometric IoU utilities for segmentation validation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean
from typing import Any, Dict, Iterable, List, Tuple

import numpy as np
from PIL import Image, ImageDraw

Point = Tuple[int, int]


def _mask(points: Iterable[Iterable[int]], size: tuple[int, int]) -> np.ndarray:
    """Rasterize a polygon into a binary mask."""
    image = Image.new("1", size, 0)
    polygon = [(int(x), int(y)) for x, y in points]
    if len(polygon) >= 3:
        ImageDraw.Draw(image).polygon(polygon, outline=1, fill=1)
    return np.asarray(image, dtype=bool)


def polygon_iou(prediction: List[List[int]], reference: List[List[int]], size: tuple[int, int]) -> float:
    """Compute polygon IoU by rasterization.

    Args:
        prediction: Predicted polygon points.
        reference: Reference polygon points.
        size: Page image size as ``(width, height)``.

    Returns:
        Intersection over Union in ``[0, 1]``.
    """
    pred_mask = _mask(prediction, size)
    ref_mask = _mask(reference, size)
    union = np.logical_or(pred_mask, ref_mask).sum()
    if union == 0:
        return 0.0
    return float(np.logical_and(pred_mask, ref_mask).sum() / union)


def evaluate_page(page_dir: Path) -> Dict[str, Any]:
    """Evaluate IoU for a page when reference polygons are available."""
    polygons_path = page_dir / "polygons.json"
    gt_path = page_dir / "ground_truth_objects.json"
    image_path = page_dir / "segmentation_input.png"
    if not (polygons_path.exists() and gt_path.exists() and image_path.exists()):
        return {"page": page_dir.name, "status": "missing_reference", "ious": []}

    predictions = json.load(polygons_path.open("r", encoding="utf-8")).get("lines", [])
    references = json.load(gt_path.open("r", encoding="utf-8"))
    with Image.open(image_path) as image:
        size = image.size

    ious = []
    for prediction, reference in zip(predictions, references):
        ref_polygon = reference.get("polygon") or reference.get("boundary") or reference.get("points")
        if prediction.get("polygon") and ref_polygon:
            ious.append(polygon_iou(prediction["polygon"], ref_polygon, size))
    return {
        "page": page_dir.name,
        "status": "ok" if ious else "no_comparable_polygons",
        "num_pairs": len(ious),
        "mean_iou": float(mean(ious)) if ious else None,
        "ious": ious,
    }


def evaluate_directory(input_dir: str = "outputs/segmentation", output_dir: str = "outputs/segmentation_iou") -> Dict[str, Any]:
    """Evaluate segmentation IoU for every available page output."""
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    candidates = [Path(input_dir)]
    candidates.extend(sorted(Path("outputs/judicial_demo").glob("page_*_canvas_*")))
    pages = [evaluate_page(path) for path in candidates if path.exists()]
    all_ious = [score for page in pages for score in page.get("ious", [])]
    report = {
        "input_dir": input_dir,
        "num_pages": len(pages),
        "num_pairs": len(all_ious),
        "mean_iou": float(mean(all_ious)) if all_ious else None,
        "pages": pages,
        "note": "Judicial Gallica pages do not include reference polygons; IoU is computed only when ground_truth_objects.json contains comparable polygons.",
    }
    with (output / "segmentation_iou_report.json").open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, ensure_ascii=False)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return report


def main() -> None:
    """Run segmentation IoU evaluation from the command line."""
    parser = argparse.ArgumentParser(description="Compute segmentation IoU when reference polygons are available.")
    parser.add_argument("--input-dir", default="outputs/segmentation")
    parser.add_argument("--output-dir", default="outputs/segmentation_iou")
    args = parser.parse_args()
    evaluate_directory(args.input_dir, args.output_dir)


if __name__ == "__main__":
    main()
