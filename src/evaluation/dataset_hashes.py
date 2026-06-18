"""Compute SHA-256 hashes for configured dataset splits."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.dataset.load_dataset import load_configured_dataset


def _sample_payload(row: Dict[str, Any]) -> bytes:
    """Serialize stable row fields for hashing."""
    payload = {
        "sample_id": str(row.get("sample_id", "")),
        "text": row.get("text", ""),
    }
    return json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")


def hash_dataset(config_path: str = "config.yaml", output_path: str = "artifacts/dataset_hashes.json") -> Dict[str, Any]:
    """Hash the train, validation, and test splits configured for HTR.

    Args:
        config_path: YAML configuration path.
        output_path: Destination JSON artifact.

    Returns:
        Mapping of split names to row counts and SHA-256 digests.
    """
    dataset = load_configured_dataset(config_path)
    result = {}
    for split_name in ("train", "validation", "test"):
        digest = hashlib.sha256()
        split = dataset[split_name]
        for row in split:
            digest.update(_sample_payload(row))
            digest.update(b"\n")
        result[split_name] = {"num_rows": len(split), "sha256": digest.hexdigest()}
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, ensure_ascii=False)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return result


def main() -> None:
    """Run dataset split hashing from the command line."""
    parser = argparse.ArgumentParser(description="Compute SHA-256 hashes for configured dataset splits.")
    parser.add_argument("--config", default="config.yaml")
    parser.add_argument("--output", default="artifacts/dataset_hashes.json")
    args = parser.parse_args()
    hash_dataset(args.config, args.output)


if __name__ == "__main__":
    main()
