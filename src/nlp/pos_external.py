"""Optional POS/lemma backends for historical French.

The preferred tools for the project are Stanza ``frm`` or pie-extended
``medieval-fr``. They are optional at runtime: if neither backend is installed,
the project falls back to deterministic local POS/lemma rules.
"""

from __future__ import annotations

from typing import Dict, List

from src.nlp.advanced_pipeline import pos_tag
from src.nlp.text_processing import simple_lemma, tokenize


def tag_with_optional_backend(text: str, backend: str = "auto") -> Dict[str, object]:
    """Tag text with Stanza/Pie if available, otherwise use local rules.

    Args:
        text: Input transcription line.
        backend: ``auto``, ``stanza``, ``pie`` or ``fallback``.

    Returns:
        Dictionary containing the backend used and token annotations.
    """
    if backend in {"auto", "stanza"}:
        try:
            return _tag_with_stanza(text)
        except Exception:
            if backend == "stanza":
                raise
    if backend in {"auto", "pie"}:
        try:
            return _tag_with_pie(text)
        except Exception:
            if backend == "pie":
                raise
    return _tag_with_fallback(text)


def _tag_with_stanza(text: str) -> Dict[str, object]:
    import stanza  # type: ignore

    pipeline = stanza.Pipeline(lang="frm", processors="tokenize,pos,lemma", tokenize_no_ssplit=True, verbose=False)
    doc = pipeline(text)
    tokens: List[Dict[str, str]] = []
    for sentence in doc.sentences:
        for word in sentence.words:
            tokens.append({"text": word.text, "lemma": word.lemma or word.text, "pos": word.upos or "X"})
    return {"backend": "stanza_frm", "tokens": tokens}


def _tag_with_pie(text: str) -> Dict[str, object]:
    # pie-extended APIs differ by installation. This function intentionally
    # isolates the optional dependency and falls back cleanly when unavailable.
    import pie_extended  # type: ignore  # noqa: F401

    raise RuntimeError("pie-extended backend is not configured in this environment")


def _tag_with_fallback(text: str) -> Dict[str, object]:
    tokens = [
        {"text": token.text, "lemma": simple_lemma(token.text), "pos": pos_tag(token)}
        for token in tokenize(text)
    ]
    return {"backend": "fallback_rules", "tokens": tokens}
