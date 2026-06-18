import argparse
import csv
import json
import sys
from pathlib import Path
from statistics import mean, median
from typing import Any, Dict, List

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[2]))


def _stats(values: List[float]) -> Dict[str, float]:
    if not values:
        return {"min": 0.0, "max": 0.0, "mean": 0.0, "median": 0.0}
    return {
        "min": float(min(values)),
        "max": float(max(values)),
        "mean": float(mean(values)),
        "median": float(median(values)),
    }


def _page_size(page_dir: Path) -> tuple[int, int] | None:
    image_path = page_dir / "segmentation_input.png"
    if not image_path.exists():
        return None
    with Image.open(image_path) as image:
        return image.size


def analyze_crop(line: Dict[str, Any], page_dir: Path, page_size: tuple[int, int] | None) -> Dict[str, Any]:
    crop_path = Path(line.get("crop_path", ""))
    if not crop_path.is_absolute():
        crop_path = Path(line.get("crop_path", ""))

    with Image.open(crop_path).convert("L") as image:
        array = np.asarray(image, dtype=np.float32)
        width, height = image.size

    contrast = float(array.std())
    mean_gray = float(array.mean())
    dark_ratio = float((array < 180).mean())
    edge_dark_ratio = 0.0
    if width >= 4:
        edge = np.concatenate([array[:, :2].ravel(), array[:, -2:].ravel()])
        edge_dark_ratio = float((edge < 160).mean())

    bbox = line.get("bbox") or [0, 0, width, height]
    touches_page_edge = False
    if page_size:
        page_width, page_height = page_size
        touches_page_edge = bbox[0] <= 2 or bbox[1] <= 2 or bbox[2] >= page_width - 2 or bbox[3] >= page_height - 2

    return {
        "page": page_dir.name,
        "order": line.get("order"),
        "id": line.get("id"),
        "crop_path": str(crop_path),
        "width": width,
        "height": height,
        "aspect_ratio": float(width / height) if height else 0.0,
        "mean_gray": mean_gray,
        "contrast": contrast,
        "dark_pixel_ratio": dark_ratio,
        "edge_dark_ratio": edge_dark_ratio,
        "empty_like": contrast < 5.0 or dark_ratio < 0.01,
        "too_small": width < 100 or height < 18,
        "possibly_truncated": touches_page_edge or edge_dark_ratio > 0.35,
        "prediction": line.get("prediction", ""),
    }


def _save_histogram(values: List[float], title: str, xlabel: str, output_path: Path) -> None:
    fig, axis = plt.subplots(figsize=(8, 4))
    axis.hist(values, bins=30)
    axis.set_title(title)
    axis.set_xlabel(xlabel)
    axis.set_ylabel("count")
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def analyze_directory(input_dir: str = "outputs/judicial_demo", output_dir: str = "outputs/crop_analysis") -> Dict[str, Any]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    rows: List[Dict[str, Any]] = []
    for page_dir in sorted(Path(input_dir).glob("page_*_canvas_*")):
        transcriptions_path = page_dir / "transcriptions.json"
        if not transcriptions_path.exists():
            continue
        page_size = _page_size(page_dir)
        lines = json.load(transcriptions_path.open("r", encoding="utf-8"))
        for line in lines:
            crop_path = Path(line.get("crop_path", ""))
            if crop_path.exists():
                rows.append(analyze_crop(line, page_dir, page_size))

    widths = [row["width"] for row in rows]
    heights = [row["height"] for row in rows]
    contrasts = [row["contrast"] for row in rows]
    dark_ratios = [row["dark_pixel_ratio"] for row in rows]

    report = {
        "input_dir": input_dir,
        "num_crops": len(rows),
        "width": _stats(widths),
        "height": _stats(heights),
        "contrast": _stats(contrasts),
        "dark_pixel_ratio": _stats(dark_ratios),
        "empty_like_count": sum(1 for row in rows if row["empty_like"]),
        "too_small_count": sum(1 for row in rows if row["too_small"]),
        "possibly_truncated_count": sum(1 for row in rows if row["possibly_truncated"]),
        "problematic_examples": [
            row
            for row in rows
            if row["empty_like"] or row["too_small"] or row["possibly_truncated"]
        ][:25],
    }

    with (output / "crop_quality_report.json").open("w", encoding="utf-8") as handle:
        json.dump({"summary": report, "crops": rows}, handle, indent=2, ensure_ascii=False)

    with (output / "crop_quality.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()) if rows else ["page"])
        writer.writeheader()
        writer.writerows(rows)

    _save_histogram(widths, "Line crop widths", "pixels", output / "crop_widths.png")
    _save_histogram(heights, "Line crop heights", "pixels", output / "crop_heights.png")
    _save_histogram(contrasts, "Line crop contrast", "grayscale std", output / "crop_contrast.png")

    with (output / "crop_quality_report.md").open("w", encoding="utf-8") as handle:
        handle.write("# Crop quality analysis\n\n")
        handle.write(f"- Crops analyzed: {report['num_crops']}\n")
        handle.write(f"- Width mean/median: {report['width']['mean']:.1f} / {report['width']['median']:.1f}px\n")
        handle.write(f"- Height mean/median: {report['height']['mean']:.1f} / {report['height']['median']:.1f}px\n")
        handle.write(f"- Contrast mean/median: {report['contrast']['mean']:.1f} / {report['contrast']['median']:.1f}\n")
        handle.write(f"- Empty-like lines: {report['empty_like_count']}\n")
        handle.write(f"- Too small lines: {report['too_small_count']}\n")
        handle.write(f"- Possibly truncated lines: {report['possibly_truncated_count']}\n\n")
        handle.write("Figures: `crop_widths.png`, `crop_heights.png`, `crop_contrast.png`.\n")

    print(json.dumps(report, indent=2, ensure_ascii=False))
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze extracted Kraken line crop quality.")
    parser.add_argument("--input-dir", default="outputs/judicial_demo")
    parser.add_argument("--output-dir", default="outputs/crop_analysis")
    args = parser.parse_args()
    analyze_directory(args.input_dir, args.output_dir)


if __name__ == "__main__":
    main()
