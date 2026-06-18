"""Exploratory data analysis for the NLP input data contract."""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.nlp.normalization import count_residual_abbreviations


def _load_rows(input_path: str) -> List[Dict[str, Any]]:
    rows = json.load(Path(input_path).open("r", encoding="utf-8"))
    if not isinstance(rows, list):
        raise ValueError("Expected a JSON list")
    return rows


def _summary(values: List[float]) -> Dict[str, float]:
    if not values:
        return {"min": 0, "max": 0, "mean": 0, "median": 0}
    return {
        "min": min(values),
        "max": max(values),
        "mean": statistics.mean(values),
        "median": statistics.median(values),
    }


def run_eda(
    input_path: str = "dataset_nlp/transcriptions.json",
    output_dir: str = "outputs/nlp_eda",
) -> Dict[str, Any]:
    """Generate EDA statistics required by the NLP brief."""
    rows = _load_rows(input_path)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    confidences = [float(row.get("confidence") or 0) for row in rows]
    line_lengths = [len(row.get("transcription") or row.get("prediction") or "") for row in rows]
    residual_abbrev = [count_residual_abbreviations(row.get("transcription") or row.get("prediction") or "") for row in rows]
    pages = Counter(str(row.get("page_id", "")) for row in rows)
    has_char_confidences = sum(1 for row in rows if row.get("char_confidences"))
    has_candidates = sum(1 for row in rows if row.get("candidates"))
    needs_review = sum(1 for row in rows if row.get("needs_review"))

    report = {
        "input_path": input_path,
        "num_lines": len(rows),
        "pages": dict(sorted(pages.items())),
        "confidence": _summary(confidences),
        "line_length_chars": _summary(line_lengths),
        "needs_review_count": needs_review,
        "needs_review_rate": needs_review / len(rows) if rows else 0,
        "residual_abbreviation_marks": {
            "total": sum(residual_abbrev),
            "lines_with_residual_marks": sum(1 for value in residual_abbrev if value > 0),
        },
        "char_confidences_available_lines": has_char_confidences,
        "candidates_available_lines": has_candidates,
        "note": (
            "char_confidences/candidates are not available in current Kraken exports; "
            "confidence-guided candidate correction is therefore documented but not applied."
        ),
    }

    with (output / "nlp_eda_report.json").open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, ensure_ascii=False)
    with (output / "nlp_eda_report.md").open("w", encoding="utf-8") as handle:
        handle.write("# NLP EDA report\n\n")
        handle.write(f"- Lines: {report['num_lines']}\n")
        handle.write(f"- Pages: {len(report['pages'])}\n")
        handle.write(f"- Confidence mean: {report['confidence']['mean']:.4f}\n")
        handle.write(f"- Confidence median: {report['confidence']['median']:.4f}\n")
        handle.write(f"- Needs review: {needs_review} ({report['needs_review_rate']:.2%})\n")
        handle.write(f"- Mean line length: {report['line_length_chars']['mean']:.1f} chars\n")
        handle.write(f"- Residual abbreviation marks: {report['residual_abbreviation_marks']['total']}\n")
        handle.write(f"- Lines with char confidences: {has_char_confidences}\n")
        handle.write(f"- Lines with candidates: {has_candidates}\n\n")
        handle.write(report["note"] + "\n")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return report


def main() -> None:
    """Run NLP EDA."""
    parser = argparse.ArgumentParser(description="Run EDA on NLP input JSON.")
    parser.add_argument("--input", default="dataset_nlp/transcriptions.json")
    parser.add_argument("--output-dir", default="outputs/nlp_eda")
    args = parser.parse_args()
    run_eda(args.input, args.output_dir)


if __name__ == "__main__":
    main()

