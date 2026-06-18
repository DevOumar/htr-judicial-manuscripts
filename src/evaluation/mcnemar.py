"""McNemar comparison for paired HTR prediction files."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Dict


def _load_by_sample(path: str) -> Dict[str, dict]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return {row["sample_id"]: row for row in csv.DictReader(handle)}


def _is_correct(row: dict, cer_threshold: float) -> bool:
    return float(row.get("cer", 1.0)) <= cer_threshold


def mcnemar_test(
    model_a_csv: str,
    model_b_csv: str,
    output_path: str = "outputs/evaluation/mcnemar_report.json",
    cer_threshold: float = 0.5,
) -> dict:
    """Run an exact/binomial McNemar-style comparison on paired samples.

    A line is considered correct when its CER is at or below `cer_threshold`.
    For small samples this report uses the continuity-corrected chi-square
    statistic as a descriptive value and an exact two-sided binomial p-value.

    Args:
        model_a_csv: Prediction CSV for model A.
        model_b_csv: Prediction CSV for model B.
        output_path: Destination JSON report.
        cer_threshold: CER threshold used to binarize correctness.

    Returns:
        McNemar contingency counts and p-value.
    """
    model_a = _load_by_sample(model_a_csv)
    model_b = _load_by_sample(model_b_csv)
    sample_ids = sorted(set(model_a).intersection(model_b))

    both_correct = 0
    both_wrong = 0
    a_correct_b_wrong = 0
    a_wrong_b_correct = 0

    for sample_id in sample_ids:
        a_ok = _is_correct(model_a[sample_id], cer_threshold)
        b_ok = _is_correct(model_b[sample_id], cer_threshold)
        if a_ok and b_ok:
            both_correct += 1
        elif not a_ok and not b_ok:
            both_wrong += 1
        elif a_ok and not b_ok:
            a_correct_b_wrong += 1
        else:
            a_wrong_b_correct += 1

    discordant = a_correct_b_wrong + a_wrong_b_correct
    if discordant:
        chi2 = (abs(a_correct_b_wrong - a_wrong_b_correct) - 1) ** 2 / discordant
        k = min(a_correct_b_wrong, a_wrong_b_correct)
        p_value = 2 * sum(math.comb(discordant, i) for i in range(k + 1)) * (0.5 ** discordant)
        p_value = min(1.0, p_value)
    else:
        chi2 = 0.0
        p_value = 1.0

    report = {
        "model_a_csv": model_a_csv,
        "model_b_csv": model_b_csv,
        "cer_threshold": cer_threshold,
        "num_paired_samples": len(sample_ids),
        "both_correct": both_correct,
        "both_wrong": both_wrong,
        "a_correct_b_wrong": a_correct_b_wrong,
        "a_wrong_b_correct": a_wrong_b_correct,
        "mcnemar_chi2_continuity_corrected": chi2,
        "exact_binomial_p_value": p_value,
        "interpretation": "Descriptive only when the paired sample is very small.",
    }
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, ensure_ascii=False)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return report


def main() -> None:
    """Run McNemar comparison from the command line."""
    parser = argparse.ArgumentParser(description="Compare two paired HTR prediction CSV files with McNemar.")
    parser.add_argument("--model-a", default="outputs/evaluation/baseline_french_predictions.csv")
    parser.add_argument("--model-b", default="outputs/evaluation/french_decoder_predictions.csv")
    parser.add_argument("--output", default="outputs/evaluation/mcnemar_report.json")
    parser.add_argument("--cer-threshold", type=float, default=0.5)
    args = parser.parse_args()
    mcnemar_test(args.model_a, args.model_b, args.output, args.cer_threshold)


if __name__ == "__main__":
    main()
