"""Validate final transcription JSON files against the project JSON Schema."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List


def _validate_with_jsonschema(instance: Any, schema: Dict[str, Any]) -> List[str]:
    """Validate with jsonschema when installed, otherwise return an install hint."""
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        return ["jsonschema is not installed; install requirements.txt to enable schema validation."]
    validator = Draft202012Validator(schema)
    return [error.message for error in validator.iter_errors(instance)]


def _candidate_files(input_path: str) -> List[Path]:
    path = Path(input_path)
    if path.is_file():
        return [path]
    return sorted(path.glob("page_*_canvas_*/transcriptions.json"))


def validate_directory(input_dir: str = "outputs/judicial_demo", schema_path: str = "schemas/transcription_schema.json") -> Dict[str, Any]:
    """Validate all judicial ``transcriptions.json`` files.

    Args:
        input_dir: Directory containing page-level judicial outputs.
        schema_path: JSON Schema path.

    Returns:
        Summary report with per-file errors.
    """
    schema = json.load(Path(schema_path).open("r", encoding="utf-8"))
    files = _candidate_files(input_dir)
    results = []
    for path in files:
        instance = json.load(path.open("r", encoding="utf-8"))
        errors = _validate_with_jsonschema(instance, schema)
        results.append({"file": str(path), "valid": not errors, "errors": errors})
    report = {
        "schema": schema_path,
        "input_dir": input_dir,
        "num_files": len(results),
        "valid_files": sum(1 for item in results if item["valid"]),
        "files": results,
    }
    output_dir = Path("outputs/data_contract_validation")
    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "data_contract_validation_report.json").open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, ensure_ascii=False)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return report


def main() -> None:
    """Run data contract validation from the command line."""
    parser = argparse.ArgumentParser(description="Validate transcription JSON files against schemas/transcription_schema.json.")
    parser.add_argument("--input-dir", default="outputs/judicial_demo")
    parser.add_argument("--schema", default="schemas/transcription_schema.json")
    args = parser.parse_args()
    validate_directory(args.input_dir, args.schema)


if __name__ == "__main__":
    main()
