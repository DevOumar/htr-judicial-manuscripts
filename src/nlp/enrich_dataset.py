"""Create an NLP-enriched dataset from line-level HTR transcriptions."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.nlp.normalization import normalize_for_nlp
from src.nlp.text_processing import normalize_text, tokenize, tokens_to_dicts


def _load_rows(input_path: str) -> List[Dict[str, Any]]:
    path = Path(input_path)
    rows = json.load(path.open("r", encoding="utf-8"))
    if not isinstance(rows, list):
        raise ValueError(f"Expected a JSON list in {input_path}")
    return rows


def enrich_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Add normalized text, tokenization, and lemmas to line rows."""
    enriched: List[Dict[str, Any]] = []
    for row in rows:
        record = dict(row)
        text = record.get("transcription") or record.get("prediction") or ""
        normalized = normalize_text(str(text))
        rule_normalized = normalize_for_nlp(normalized)
        tokens = tokenize(rule_normalized.text)
        token_dicts = tokens_to_dicts(tokens)
        word_tokens = [token for token in token_dicts if token["type"] in {"word", "number"}]
        record["normalized_transcription"] = normalized
        record["rule_normalized_transcription"] = rule_normalized.text
        record["normalization_rules_applied"] = rule_normalized.applied_rules
        record["tokens"] = token_dicts
        record["lemmas"] = [str(token["lemma"]) for token in word_tokens]
        record["num_tokens"] = len(token_dicts)
        record["num_word_tokens"] = len(word_tokens)
        enriched.append(record)
    return enriched


def build_statistics(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute corpus-level NLP statistics."""
    token_counter: Counter[str] = Counter()
    lemma_counter: Counter[str] = Counter()
    page_counts: Counter[str] = Counter()
    review_rows = 0
    for row in rows:
        page_counts[str(row.get("page_id", ""))] += 1
        if row.get("needs_review"):
            review_rows += 1
        for token in row.get("tokens", []):
            if token.get("type") in {"word", "number"}:
                token_counter[str(token.get("normalized", ""))] += 1
                lemma_counter[str(token.get("lemma", ""))] += 1

    total_word_tokens = sum(token_counter.values())
    return {
        "num_lines": len(rows),
        "num_pages": len(page_counts),
        "lines_by_page": dict(sorted(page_counts.items())),
        "lines_needs_review": review_rows,
        "total_word_tokens": total_word_tokens,
        "unique_tokens": len(token_counter),
        "unique_lemmas": len(lemma_counter),
        "top_tokens": token_counter.most_common(30),
        "top_lemmas": lemma_counter.most_common(30),
    }


def write_vocab_csv(counter_pairs: List[tuple[str, int]], output_path: Path, field: str) -> None:
    """Write a frequency list to CSV."""
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=[field, "count"])
        writer.writeheader()
        for value, count in counter_pairs:
            writer.writerow({field: value, "count": count})


def enrich_dataset(
    input_path: str = "dataset_nlp/transcriptions.json",
    output_dir: str = "dataset_nlp/nlp",
) -> Dict[str, Any]:
    """Generate NLP-enriched JSON and lexical statistics.

    Args:
        input_path: Line-level transcription JSON.
        output_dir: Destination directory for NLP outputs.

    Returns:
        Statistics report.
    """
    rows = _load_rows(input_path)
    enriched = enrich_rows(rows)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    enriched_path = output / "transcriptions_enriched.json"
    with enriched_path.open("w", encoding="utf-8") as handle:
        json.dump(enriched, handle, indent=2, ensure_ascii=False)

    for page_id in sorted({str(row.get("page_id", "")) for row in enriched}):
        page_rows = [row for row in enriched if str(row.get("page_id", "")) == page_id]
        with (output / f"{page_id}_nlp.json").open("w", encoding="utf-8") as handle:
            json.dump(page_rows, handle, indent=2, ensure_ascii=False)

    stats = build_statistics(enriched)
    with (output / "nlp_statistics.json").open("w", encoding="utf-8") as handle:
        json.dump(stats, handle, indent=2, ensure_ascii=False)

    write_vocab_csv(stats["top_tokens"], output / "top_tokens.csv", "token")
    write_vocab_csv(stats["top_lemmas"], output / "top_lemmas.csv", "lemma")

    with (output / "nlp_report.md").open("w", encoding="utf-8") as handle:
        handle.write("# NLP report\n\n")
        handle.write(f"- Lines: {stats['num_lines']}\n")
        handle.write(f"- Pages: {stats['num_pages']}\n")
        handle.write(f"- Lines needing review: {stats['lines_needs_review']}\n")
        handle.write(f"- Word tokens: {stats['total_word_tokens']}\n")
        handle.write(f"- Unique tokens: {stats['unique_tokens']}\n")
        handle.write(f"- Unique lemmas: {stats['unique_lemmas']}\n\n")
        handle.write("## Method\n\n")
        handle.write(
            "The pipeline applies Unicode NFC normalization, deterministic regex tokenization, "
            "and conservative historical-French lemmatization rules. Lemmas are intended for "
            "exploration, not for philological final annotation.\n\n"
        )
        handle.write("## Top lemmas\n\n")
        for lemma, count in stats["top_lemmas"][:20]:
            handle.write(f"- `{lemma}`: {count}\n")

    print(json.dumps({"output_dir": str(output), **stats}, indent=2, ensure_ascii=False))
    return stats


def main() -> None:
    """Run the NLP enrichment pipeline."""
    parser = argparse.ArgumentParser(description="Enrich HTR transcriptions with NLP annotations.")
    parser.add_argument("--input", default="dataset_nlp/transcriptions.json")
    parser.add_argument("--output-dir", default="dataset_nlp/nlp")
    args = parser.parse_args()
    enrich_dataset(args.input, args.output_dir)


if __name__ == "__main__":
    main()
