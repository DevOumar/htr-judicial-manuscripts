from src.htr.metrics import cer
from src.nlp.normalization import normalize_for_nlp


def test_nlp_normalization_expands_abbreviations() -> None:
    result = normalize_for_nlp("Le Roy q~ la Reyne")

    assert result.text == "Le Roi que la Reine"
    assert "tilde_abbreviations" in result.applied_rules
    assert "frequent_historical_graphies" in result.applied_rules


def test_rule_normalization_does_not_degrade_reference_cer() -> None:
    reference = "Le Roi que la Reine"
    raw = "Le Roy q~ la Reyne"
    normalized = normalize_for_nlp(raw).text

    assert cer(reference, normalized) <= cer(reference, raw)

