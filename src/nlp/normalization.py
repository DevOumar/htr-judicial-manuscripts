"""Deterministic NLP normalization rules for historical French HTR output."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Callable, List


@dataclass(frozen=True)
class NormalizationResult:
    """Result of deterministic text normalization."""

    text: str
    applied_rules: List[str]


def _nfc(text: str) -> str:
    return unicodedata.normalize("NFC", text or "")


def _normalize_spacing(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _normalize_apostrophes(text: str) -> str:
    return text.replace("’", "'").replace("`", "'").replace("´", "'")


def _expand_tilde_abbreviations(text: str) -> str:
    replacements = {
        "q~": "que",
        "Q~": "Que",
        "qu~": "que",
        "Qu~": "Que",
        "p~": "par",
        "P~": "Par",
        "n~re": "notre",
        "N~re": "Notre",
        "v~re": "votre",
        "V~re": "Votre",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    return text


def _resolve_combining_nasal_tilde(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text)
    replacements = {
        "a\u0303": "an",
        "A\u0303": "An",
        "e\u0303": "en",
        "E\u0303": "En",
        "i\u0303": "in",
        "I\u0303": "In",
        "o\u0303": "on",
        "O\u0303": "On",
        "u\u0303": "un",
        "U\u0303": "Un",
    }
    for source, target in replacements.items():
        decomposed = decomposed.replace(source, target)
    return unicodedata.normalize("NFC", decomposed)


def _normalize_frequent_graphies(text: str) -> str:
    replacements = {
        r"\broy\b": "roi",
        r"\bRoy\b": "Roi",
        r"\breyne\b": "reine",
        r"\bReyne\b": "Reine",
        r"\bmil\b": "mille",
        r"\bMil\b": "Mille",
        r"\bcens\b": "cent",
        r"\bCens\b": "Cent",
        r"\bestoit\b": "etait",
        r"\bestoient\b": "etaient",
        r"\bavoit\b": "avait",
        r"\bavoient\b": "avaient",
    }
    for pattern, replacement in replacements.items():
        text = re.sub(pattern, replacement, text)
    return text


RULES: list[tuple[str, Callable[[str], str]]] = [
    ("unicode_nfc", _nfc),
    ("apostrophes", _normalize_apostrophes),
    ("tilde_abbreviations", _expand_tilde_abbreviations),
    ("nasal_tilde", _resolve_combining_nasal_tilde),
    ("frequent_historical_graphies", _normalize_frequent_graphies),
    ("spacing", _normalize_spacing),
]


def normalize_for_nlp(text: str) -> NormalizationResult:
    """Apply deterministic normalization rules and report which changed text."""
    current = text or ""
    applied: List[str] = []
    for name, rule in RULES:
        new_value = rule(current)
        if new_value != current:
            applied.append(name)
        current = new_value
    return NormalizationResult(text=current, applied_rules=applied)


def count_residual_abbreviations(text: str) -> int:
    """Count residual abbreviation marks mentioned in the NLP brief."""
    return len(re.findall(r"[~ꝑꝗꝙ]", text or ""))

