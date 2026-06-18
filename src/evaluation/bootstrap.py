
"""Bootstrap confidence intervals for HTR CER and WER."""

from __future__ import annotations

import argparse
import csv
import json
import random
import sys
from pathlib import Path
from typing import Callable, Dict, List

import numpy as np

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.htr.metrics import average_cer, corpus_wer


def bootstrap_metric(values: List[float], n: int = 1000, seed: int = 42) -> Dict[str, float]:
    """Bootstrap a mean score and its 95 percent confidence interval.

    Args:
        values: Per-sample metric values.
        n: Number of bootstrap resamples.
        seed: Random seed for reproducibility.

    Returns:
        Mean, lower CI bound, and upper CI bound.
    """
    rng = random.Random(seed)
    scores = []
    for _ in range(n):
        sample = [rng.choice(values) for _ in values]
        scores.append(float(np.mean(sample)))
    return {
        "mean": float(np.mean(values)) if values else 0.0,
        "ci95_low": float(np.percentile(scores, 2.5)) if scores else 0.0,
        "ci95_high": float(np.percentile(scores, 97.5)) if scores else 0.0,
        "n_bootstrap": n,
    }


def bootstrap_corpus_metric(
    references: List[str],
    predictions: List[str],
    metric: Callable[[List[str], List[str]], float],
    n: int = 1000,
    seed: int = 42,
) -> Dict[str, float]:
    """Bootstrap a corpus-level text metric from aligned prediction pairs."""
    rng = random.Random(seed)
    indices = list(range(len(references)))
    scores = []
    for _ in range(n):
        sample_indices = [rng.choice(indices) for _ in indices]
        sample_refs = [references[index] for index in sample_indices]
        sample_preds = [predictions[index] for index in sample_indices]
        scores.append(metric(sample_refs, sample_preds))
    observed = metric(references, predictions) if references else 0.0
    return {
        "mean": float(observed),
        "ci95_low": float(np.percentile(scores, 2.5)) if scores else 0.0,
        "ci95_high": float(np.percentile(scores, 97.5)) if scores else 0.0,
        "n_bootstrap": n,
    }


def bootstrap_predictions_csv(
    predictions_csv: str,
    output_path: str = "outputs/evaluation/bootstrap_cer_wer.json",
    n: int = 1000,
    seed: int = 42,
) -> Dict[str, Dict[str, float]]:
    """Compute CER/WER bootstrap intervals from an evaluation CSV.

    Args:
        predictions_csv: CSV containing ``reference`` and ``prediction`` columns.
        output_path: Destination JSON report.
        n: Number of bootstrap samples.
        seed: Random seed.

    Returns:
        Bootstrap report for CER and WER.
    """
    rows = list(csv.DictReader(Path(predictions_csv).open("r", encoding="utf-8")))
    references = [row["reference"] for row in rows]
    predictions = [row["prediction"] for row in rows]
    report = {
        "input": predictions_csv,
        "num_samples": len(rows),
        "cer": bootstrap_corpus_metric(references, predictions, average_cer, n, seed),
        "wer": bootstrap_corpus_metric(references, predictions, corpus_wer, n, seed),
    }
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, ensure_ascii=False)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return report


def main() -> None:
    """Run CER/WER bootstrap from the command line."""
    parser = argparse.ArgumentParser(description="Compute bootstrap 95% CI for CER/WER from predictions CSV.")
    parser.add_argument("--predictions", default="outputs/evaluation/french_decoder_predictions.csv")
    parser.add_argument("--output", default="outputs/evaluation/bootstrap_cer_wer.json")
    parser.add_argument("--n", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    bootstrap_predictions_csv(args.predictions, args.output, args.n, args.seed)


if __name__ == "__main__":
    main()
