import re
import unicodedata


def repair_mojibake(text: str) -> str:
    if not any(marker in text for marker in ("Ã", "Â", "á", "â")):
        return text
    try:
        repaired = text.encode("latin-1").decode("utf-8")
    except UnicodeError:
        return text
    return repaired


def normalize_transcription(text: str, mode: str = "readable") -> str:
    if not text:
        return ""

    text = repair_mojibake(text)
    text = unicodedata.normalize("NFKC", text)

    if mode == "none":
        return text

    replacements = {
        "⁊": " et ",
        "\u204a": " et ",
        "ſ": "s",
        "ꝑ": "per",
        "ꝓ": "pro",
        "�": "",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)

    if mode == "readable":
        text = "".join(char for char in text if unicodedata.category(char) != "Mn")

    text = re.sub(r"\s+", " ", text)
    return text.strip()
