"""Quality metadata helpers for HTR line predictions."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict

import numpy as np
from PIL import Image


REPEATED_CHARS = re.compile(r"(.)\1{3,}")


def estimate_confidence(line: Dict[str, Any]) -> float:
    """Estimate a line-level confidence when model probabilities are unavailable.

    Args:
        line: Serialized line dictionary with optional prediction, confidence,
            crop path, and bounding box fields.

    Returns:
        A float in ``[0, 1]``. Existing model confidence is preserved when
        present; otherwise a conservative heuristic score is computed.
    """
    if line.get("confidence") is not None:
        return max(0.0, min(1.0, float(line["confidence"])))

    prediction = (line.get("prediction") or "").strip()
    score = 0.55
    if not prediction:
        score -= 0.45
    if len(prediction) < 3:
        score -= 0.20
    if REPEATED_CHARS.search(prediction):
        score -= 0.25

    crop_path = Path(line.get("crop_path", ""))
    if crop_path.exists():
        with Image.open(crop_path).convert("L") as image:
            array = np.asarray(image, dtype=np.float32)
            width, height = image.size
        if width < 100 or height < 18:
            score -= 0.15
        if float(array.std()) < 12.0:
            score -= 0.15

    return round(max(0.01, min(0.99, score)), 4)


def should_review(line: Dict[str, Any], confidence_threshold: float = 0.50) -> bool:
    """Decide whether a predicted line should be manually reviewed.

    Args:
        line: Serialized line dictionary.
        confidence_threshold: Minimum acceptable confidence.

    Returns:
        ``True`` when the line is short, repetitive, low confidence, or has a
        visibly weak crop according to simple deterministic heuristics.
    """
    prediction = (line.get("prediction") or "").strip()
    confidence = estimate_confidence(line)
    if confidence < confidence_threshold or len(prediction) < 3:
        return True
    if REPEATED_CHARS.search(prediction):
        return True
    crop_path = Path(line.get("crop_path", ""))
    if crop_path.exists():
        with Image.open(crop_path).convert("L") as image:
            width, height = image.size
            contrast = float(np.asarray(image, dtype=np.float32).std())
        if width < 100 or height < 18 or contrast < 12.0:
            return True
    return False


def enrich_line_quality(line: Dict[str, Any], model_name: str | None = None) -> Dict[str, Any]:
    """Add MD5-required quality fields to a serialized line.

    Args:
        line: Line metadata and prediction.
        model_name: Optional model identifier to store with the line.

    Returns:
        A copy of ``line`` with ``transcription``, ``confidence``,
        ``needs_review``, and stable identifier aliases.
    """
    enriched = dict(line)
    enriched["line_id"] = enriched.get("line_id") or enriched.get("id")
    enriched["transcription"] = enriched.get("prediction", "")
    enriched["confidence"] = estimate_confidence(enriched)
    enriched["needs_review"] = should_review(enriched)
    if model_name:
        enriched["model_name"] = model_name
    return enriched


def enrich_transcription_file(path: str | Path) -> int:
    """Enrich an existing ``transcriptions.json`` file in place.

    Args:
        path: Path to a page-level transcription JSON list.

    Returns:
        Number of line records updated.
    """
    import json

    json_path = Path(path)
    rows = json.load(json_path.open("r", encoding="utf-8"))
    page_id = json_path.parent.name
    model_name = "models/trocr-catmus-french-decoder/final"
    updated = []
    for row in rows:
        row.setdefault("page_id", page_id)
        row.setdefault("image_id", page_id)
        row.setdefault("source_image", str(json_path.parent / "segmentation_input.png"))
        updated.append(enrich_line_quality(row, model_name))
    with json_path.open("w", encoding="utf-8") as handle:
        json.dump(updated, handle, indent=2, ensure_ascii=False)
    return len(updated)


def main() -> None:
    """Enrich every judicial demo transcription file with quality metadata."""
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Add confidence and needs_review flags to transcription JSON files.")
    parser.add_argument("--input-dir", default="outputs/judicial_demo")
    args = parser.parse_args()

    counts = {}
    for path in sorted(Path(args.input_dir).glob("page_*_canvas_*/transcriptions.json")):
        counts[str(path)] = enrich_transcription_file(path)
    print(json.dumps(counts, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
