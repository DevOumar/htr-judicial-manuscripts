import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator


def test_dataset_nlp_matches_transcription_schema() -> None:
    schema_path = Path("schemas/transcription_schema.json")
    dataset_path = Path("dataset_nlp/transcriptions.json")
    if not dataset_path.exists():
        pytest.skip("dataset_nlp/transcriptions.json has not been generated yet.")

    schema = json.load(schema_path.open("r", encoding="utf-8"))
    data = json.load(dataset_path.open("r", encoding="utf-8"))
    errors = list(Draft202012Validator(schema).iter_errors(data))

    assert not errors
    assert len(data) > 0
    assert all("polygon" in row for row in data)
    assert all("confidence" in row for row in data)

