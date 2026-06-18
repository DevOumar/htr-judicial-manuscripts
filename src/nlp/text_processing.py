"""Text normalization, tokenization, and conservative lemmatization."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Dict, Iterable, List


TOKEN_RE = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)?|\d+|[^\w\s]", re.UNICODE)

HISTORICAL_LEMMA_MAP: Dict[str, str] = {
    "roy": "roi",
    "roye": "roi",
    "reyn": "reine",
    "reyne": "reine",
    "saict": "sait",
    "sainct": "saint",
    "ledit": "le dit",
    "ladite": "la dite",
    "lesdits": "les dits",
    "lesdites": "les dites",
    "audit": "au dit",
    "auxdits": "aux dits",
    "iceluy": "celui",
    "icelle": "celle",
    "iceux": "ceux",
    "iceulx": "ceux",
    "cens": "cent",
    "mil": "mille",
    "sixiesme": "sixieme",
    "sepmiesme": "septieme",
    "huict": "huit",
    "faict": "fait",
    "faicts": "fait",
    "estre": "etre",
    "estoit": "etre",
    "estoient": "etre",
    "avoit": "avoir",
    "avoient": "avoir",
    "auroit": "avoir",
    "auroient": "avoir",
    "demeureroit": "demeurer",
    "jouisoient": "jouir",
    "conseil": "conseil",
    "conseit": "conseil",
    "chambre": "chambre",
    "chambres": "chambre",
}


@dataclass(frozen=True)
class TokenRecord:
    """Structured token produced by the NLP pipeline."""

    text: str
    normalized: str
    lemma: str
    token_type: str
    start: int
    end: int


def normalize_text(text: str) -> str:
    """Normalize text for deterministic downstream NLP.

    Args:
        text: Raw HTR transcription.

    Returns:
        NFC-normalized text with harmonized apostrophes and whitespace.
    """
    normalized = unicodedata.normalize("NFC", text or "")
    normalized = normalized.replace("’", "'")
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def normalize_token(token: str) -> str:
    """Normalize a single token without removing accents."""
    token = normalize_text(token).lower()
    token = token.replace("ſ", "s")
    return token


def token_type(token: str) -> str:
    """Classify token as word, number, punctuation, or unknown."""
    if re.fullmatch(r"[^\W\d_]+(?:[''][^\W\d_]+)?", token, re.UNICODE):
        return "word"
    if token.isdigit():
        return "number"
    if re.fullmatch(r"[^\w\s]", token, re.UNICODE):
        return "punct"
    return "unknown"


def simple_lemma(token: str) -> str:
    """Return a conservative lemma for OCR output and historical French.

    This is intentionally cautious. It maps frequent early modern forms and
    common OCR variants, but avoids aggressive stemming that would damage legal
    names and places.
    """
    normalized = normalize_token(token)
    if not normalized:
        return ""
    if normalized in HISTORICAL_LEMMA_MAP:
        return HISTORICAL_LEMMA_MAP[normalized]
    if "'" in normalized:
        prefix, suffix = normalized.rsplit("'", 1)
        if prefix in {"l", "d", "qu", "n", "s"} and suffix:
            return simple_lemma(suffix)
    if len(normalized) > 4 and normalized.endswith("es"):
        singular = normalized[:-2]
        if singular in HISTORICAL_LEMMA_MAP:
            return HISTORICAL_LEMMA_MAP[singular]
        return singular
    if len(normalized) > 4 and normalized.endswith("s"):
        singular = normalized[:-1]
        if singular in HISTORICAL_LEMMA_MAP:
            return HISTORICAL_LEMMA_MAP[singular]
    return normalized


def tokenize(text: str) -> List[TokenRecord]:
    """Tokenize and lemmatize one transcription line.

    Args:
        text: HTR transcription.

    Returns:
        Token records preserving character offsets.
    """
    normalized_text = normalize_text(text)
    records: List[TokenRecord] = []
    for match in TOKEN_RE.finditer(normalized_text):
        raw = match.group(0)
        kind = token_type(raw)
        normalized = normalize_token(raw)
        lemma = simple_lemma(raw) if kind in {"word", "number"} else normalized
        records.append(
            TokenRecord(
                text=raw,
                normalized=normalized,
                lemma=lemma,
                token_type=kind,
                start=match.start(),
                end=match.end(),
            )
        )
    return records


def tokens_to_dicts(tokens: Iterable[TokenRecord]) -> List[Dict[str, object]]:
    """Serialize token records for JSON export."""
    return [
        {
            "text": token.text,
            "normalized": token.normalized,
            "lemma": token.lemma,
            "type": token.token_type,
            "start": token.start,
            "end": token.end,
        }
        for token in tokens
    ]
