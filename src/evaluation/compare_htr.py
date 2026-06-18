import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[2]))


def _load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _load_predictions(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def build_report(
    output_dir: str = "outputs/evaluation",
    report_path: str = "outputs/evaluation/htr_improvement_report.md",
    baseline_name: str = "baseline",
    improved_name: str = "improved",
) -> Path:
    output = Path(output_dir)
    baseline_metrics = _load_json(output / f"{baseline_name}_metrics.json")
    improved_metrics = _load_json(output / f"{improved_name}_metrics.json")
    baseline_predictions = _load_predictions(output / f"{baseline_name}_predictions.csv")
    improved_predictions = _load_predictions(output / f"{improved_name}_predictions.csv")

    rows = []
    for base, improved in zip(baseline_predictions, improved_predictions):
        rows.append(
            {
                "sample_id": improved["sample_id"],
                "reference": improved["reference"],
                "baseline": base["prediction"],
                "improved": improved["prediction"],
                "baseline_cer": float(base["cer"]),
                "improved_cer": float(improved["cer"]),
                "delta": float(base["cer"]) - float(improved["cer"]),
            }
        )

    best = sorted(rows, key=lambda row: row["delta"], reverse=True)[:3]
    worst = sorted(rows, key=lambda row: row["improved_cer"], reverse=True)[:3]

    report = Path(report_path)
    report.parent.mkdir(parents=True, exist_ok=True)
    with report.open("w", encoding="utf-8") as handle:
        handle.write("# HTR improvement report\n\n")
        handle.write("## Setup\n\n")
        handle.write(f"- Baseline output: `{baseline_name}`\n")
        handle.write(f"- Fine-tuned output: `{improved_name}`\n")
        handle.write("- Note: negative deltas mean the fine-tuned model is worse on the measured sample.\n\n")
        handle.write("## Metrics\n\n")
        handle.write("| Model | CER | WER | Samples |\n")
        handle.write("| --- | ---: | ---: | ---: |\n")
        handle.write(
            f"| Baseline | {baseline_metrics['cer']:.4f} | {baseline_metrics['wer']:.4f} | {baseline_metrics['num_samples']} |\n"
        )
        handle.write(
            f"| Fine-tuned | {improved_metrics['cer']:.4f} | {improved_metrics['wer']:.4f} | {improved_metrics['num_samples']} |\n\n"
        )
        handle.write(
            f"CER delta: {baseline_metrics['cer'] - improved_metrics['cer']:.4f}. "
            f"WER delta: {baseline_metrics['wer'] - improved_metrics['wer']:.4f}.\n\n"
        )

        handle.write("## Best improvements\n\n")
        for row in best:
            handle.write(f"### {row['sample_id']}\n\n")
            handle.write(f"- Reference: `{row['reference']}`\n")
            handle.write(f"- Baseline: `{row['baseline']}`\n")
            handle.write(f"- Fine-tuned: `{row['improved']}`\n")
            handle.write(f"- CER: {row['baseline_cer']:.4f} -> {row['improved_cer']:.4f}\n\n")

        handle.write("## Remaining failures\n\n")
        for row in worst:
            handle.write(f"### {row['sample_id']}\n\n")
            handle.write(f"- Reference: `{row['reference']}`\n")
            handle.write(f"- Fine-tuned: `{row['improved']}`\n")
            handle.write(f"- CER: {row['improved_cer']:.4f}\n\n")

    print(report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a markdown report comparing baseline and fine-tuned HTR outputs.")
    parser.add_argument("--output-dir", default="outputs/evaluation")
    parser.add_argument("--report-path", default="outputs/evaluation/htr_improvement_report.md")
    parser.add_argument("--baseline-name", default="baseline")
    parser.add_argument("--improved-name", default="improved")
    args = parser.parse_args()
    build_report(args.output_dir, args.report_path, args.baseline_name, args.improved_name)


if __name__ == "__main__":
    main()
