import json
from pathlib import Path

import pytest


def test_reference_cer_regression_threshold() -> None:
    metrics_path = Path("outputs/evaluation/french_decoder_metrics.json")
    if not metrics_path.exists():
        pytest.skip("Reference metrics artifact is not available.")

    metrics = json.load(metrics_path.open("r", encoding="utf-8"))
    assert metrics["cer"] <= 0.75
    assert metrics["wer"] <= 1.0

