"""Create deterministic NLP train/validation/test splits and SHA-256 hashes."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
from pathlib import Path
from typing import Any, Dict, List

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[2]))


def _canonical_hash(rows: List[Dict[str, Any]]) -> str:
    payload = json.dumps(rows, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def create_splits(
    input_path: str = "dataset_nlp/transcriptions.json",
    output_dir: str = "dataset_nlp/splits",
    hash_output: str = "artifacts/nlp_dataset_hashes.json",
    seed: int = 42,
) -> Dict[str, Any]:
    """Create deterministic page-stratified NLP splits.

    The current judicial corpus has one century and one document type, so the
    practical stratification key is page_id. The seed is fixed for
    reproducibility.
    """
    rows = json.load(Path(input_path).open("r", encoding="utf-8"))
    rng = random.Random(seed)

    by_page: Dict[str, List[Dict[str, Any]]] = {}
    for row in rows:
        by_page.setdefault(str(row.get("page_id", "")), []).append(row)

    splits = {"train": [], "validation": [], "test": []}
    for page_id in sorted(by_page):
        page_rows = sorted(by_page[page_id], key=lambda item: int(item.get("order", 0)))
        rng.shuffle(page_rows)
        n = len(page_rows)
        train_end = int(n * 0.7)
        val_end = train_end + int(n * 0.15)
        splits["train"].extend(page_rows[:train_end])
        splits["validation"].extend(page_rows[train_end:val_end])
        splits["test"].extend(page_rows[val_end:])

    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    hash_report = {"seed": seed, "input_path": input_path, "splits": {}}
    for name, split_rows in splits.items():
        split_rows.sort(key=lambda item: (str(item.get("page_id", "")), int(item.get("order", 0))))
        path = output / f"{name}.json"
        with path.open("w", encoding="utf-8") as handle:
            json.dump(split_rows, handle, indent=2, ensure_ascii=False)
        hash_report["splits"][name] = {
            "path": str(path),
            "num_rows": len(split_rows),
            "sha256": _canonical_hash(split_rows),
        }

    hash_path = Path(hash_output)
    hash_path.parent.mkdir(parents=True, exist_ok=True)
    with hash_path.open("w", encoding="utf-8") as handle:
        json.dump(hash_report, handle, indent=2, ensure_ascii=False)
    print(json.dumps(hash_report, indent=2, ensure_ascii=False))
    return hash_report


def main() -> None:
    """Run split creation."""
    parser = argparse.ArgumentParser(description="Create deterministic NLP splits.")
    parser.add_argument("--input", default="dataset_nlp/transcriptions.json")
    parser.add_argument("--output-dir", default="dataset_nlp/splits")
    parser.add_argument("--hash-output", default="artifacts/nlp_dataset_hashes.json")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    create_splits(args.input, args.output_dir, args.hash_output, args.seed)


if __name__ == "__main__":
    main()

