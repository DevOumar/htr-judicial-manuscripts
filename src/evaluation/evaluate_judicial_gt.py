"""Evaluate HTR predictions against manually transcribed judicial ground truth."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.htr.metrics import average_cer, cer, corpus_wer


def _load_predictions(input_dir: str) -> Dict[tuple[str, str], Dict[str, Any]]:
    predictions: Dict[tuple[str, str], Dict[str, Any]] = {}
    paths = sorted(Path(input_dir).glob("page_*_canvas_*/transcriptions.json"))
    if not paths:
        paths = sorted(Path(input_dir).glob("page_*_canvas_*/transcriptions_kraken.json"))
    for path in paths:
        page_id = path.parent.name
        rows = json.load(path.open("r", encoding="utf-8"))
        for row in rows:
            line_id = row.get("line_id") or row.get("id")
            predictions[(page_id, line_id)] = row
    return predictions


def evaluate_ground_truth(
    gt_csv: str = "data/judicial_gt/judicial_gt_template.csv",
    predictions_dir: str = "outputs/judicial_demo",
    output_path: str = "outputs/judicial_gt_evaluation/judicial_gt_metrics.json",
) -> Dict[str, Any]:
    """Compute CER/WER for rows with non-empty manual references.

    Args:
        gt_csv: CSV containing page_id, line_id, crop_path, reference.
        predictions_dir: Judicial demo output directory with transcriptions.
        output_path: Destination metrics JSON.

    Returns:
        Evaluation report.
    """
    predictions = _load_predictions(predictions_dir)
    gt_rows = list(csv.DictReader(Path(gt_csv).open("r", encoding="utf-8")))
    rows = []
    references: List[str] = []
    hypotheses: List[str] = []
    missing_predictions = 0

    for row in gt_rows:
        reference = (row.get("reference") or "").strip()
        if not reference:
            continue
        key = (row["page_id"], row["line_id"])
        prediction_row = predictions.get(key)
        if not prediction_row:
            missing_predictions += 1
            continue
        hypothesis = prediction_row.get("transcription") or prediction_row.get("prediction") or ""
        row_cer = cer(reference, hypothesis)
        rows.append(
            {
                "page_id": row["page_id"],
                "line_id": row["line_id"],
                "crop_path": row["crop_path"],
                "reference": reference,
                "prediction": hypothesis,
                "cer": row_cer,
                "reference_length": len(reference),
                "prediction_length": len(hypothesis),
            }
        )
        references.append(reference)
        hypotheses.append(hypothesis)

    report = {
        "gt_csv": gt_csv,
        "predictions_dir": predictions_dir,
        "num_template_rows": len(gt_rows),
        "num_evaluated_rows": len(rows),
        "missing_predictions": missing_predictions,
        "cer": average_cer(references, hypotheses),
        "wer": corpus_wer(references, hypotheses),
        "examples_worst_cer": sorted(rows, key=lambda item: item["cer"], reverse=True)[:20],
    }
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, ensure_ascii=False)
    with (output.parent / "judicial_gt_predictions.csv").open("w", encoding="utf-8", newline="") as handle:
        fieldnames = list(rows[0].keys()) if rows else ["page_id", "line_id", "reference", "prediction", "cer"]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps({key: value for key, value in report.items() if key != "examples_worst_cer"}, indent=2, ensure_ascii=False))
    return report


def main() -> None:
    """Run judicial GT evaluation from the command line."""
    parser = argparse.ArgumentParser(description="Evaluate judicial HTR predictions against manual ground truth.")
    parser.add_argument("--gt", default="data/judicial_gt/judicial_gt_template.csv")
    parser.add_argument("--predictions-dir", default="outputs/judicial_demo")
    parser.add_argument("--output", default="outputs/judicial_gt_evaluation/judicial_gt_metrics.json")
    args = parser.parse_args()
    evaluate_ground_truth(args.gt, args.predictions_dir, args.output)


if __name__ == "__main__":
    main()
