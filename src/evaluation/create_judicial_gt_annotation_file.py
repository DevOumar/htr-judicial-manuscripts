"""Create a manual GT annotation CSV with model predictions as assistance."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[2]))


def _load_predictions(predictions_dir: str) -> Dict[tuple[str, str], Dict[str, Any]]:
    predictions: Dict[tuple[str, str], Dict[str, Any]] = {}
    for path in sorted(Path(predictions_dir).glob("page_*_canvas_*/transcriptions.json")):
        page_id = path.parent.name
        rows = json.load(path.open("r", encoding="utf-8"))
        for row in rows:
            line_id = row.get("line_id") or row.get("id")
            predictions[(page_id, str(line_id))] = row
    return predictions


def create_annotation_file(
    template_csv: str = "data/judicial_gt/judicial_gt_template.csv",
    predictions_dir: str = "outputs/judicial_demo",
    output_csv: str = "data/judicial_gt/judicial_gt_annotation_assisted.csv",
) -> Dict[str, Any]:
    """Create an annotation CSV that keeps reference empty for manual work.

    Args:
        template_csv: Existing GT template with selected line IDs.
        predictions_dir: Directory containing final HTR predictions.
        output_csv: Destination annotation CSV.

    Returns:
        Summary report.
    """
    predictions = _load_predictions(predictions_dir)
    template_rows = list(csv.DictReader(Path(template_csv).open("r", encoding="utf-8")))
    output = Path(output_csv)
    output.parent.mkdir(parents=True, exist_ok=True)

    missing = 0
    fieldnames = [
        "page_id",
        "line_id",
        "order",
        "crop_path",
        "prediction",
        "confidence",
        "needs_review",
        "reference",
        "notes",
    ]
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in template_rows:
            key = (row["page_id"], row["line_id"])
            prediction = predictions.get(key)
            if prediction is None:
                missing += 1
                prediction = {}
            writer.writerow(
                {
                    "page_id": row["page_id"],
                    "line_id": row["line_id"],
                    "order": prediction.get("order", ""),
                    "crop_path": row["crop_path"],
                    "prediction": prediction.get("transcription") or prediction.get("prediction", ""),
                    "confidence": prediction.get("confidence", ""),
                    "needs_review": prediction.get("needs_review", ""),
                    "reference": row.get("reference", ""),
                    "notes": "",
                }
            )

    report = {
        "template_csv": template_csv,
        "predictions_dir": predictions_dir,
        "output_csv": str(output),
        "num_rows": len(template_rows),
        "missing_predictions": missing,
        "warning": "The reference column is intentionally not auto-filled.",
    }
    with (output.parent / "judicial_gt_annotation_report.json").open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, ensure_ascii=False)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return report


def main() -> None:
    """Run annotation CSV generation."""
    parser = argparse.ArgumentParser(description="Create assisted judicial GT annotation CSV.")
    parser.add_argument("--template", default="data/judicial_gt/judicial_gt_template.csv")
    parser.add_argument("--predictions-dir", default="outputs/judicial_demo")
    parser.add_argument("--output", default="data/judicial_gt/judicial_gt_annotation_assisted.csv")
    args = parser.parse_args()
    create_annotation_file(args.template, args.predictions_dir, args.output)


if __name__ == "__main__":
    main()
