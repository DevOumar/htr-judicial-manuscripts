from src.nlp.text_processing import normalize_text, simple_lemma, tokenize


def test_tokenize_and_lemmatize_historical_forms() -> None:
    text = "Le Roy et la Reyne, mil six cens trente huit."
    tokens = tokenize(text)
    lemmas = [token.lemma for token in tokens if token.token_type in {"word", "number"}]

    assert normalize_text("  Le   Roy  ") == "Le Roy"
    assert "roi" in lemmas
    assert "reine" in lemmas
    assert "mille" in lemmas
    assert "cent" in lemmas


def test_simple_lemma_is_conservative_for_unknown_words() -> None:
    assert simple_lemma("Parlement") == "parlement"
    assert simple_lemma("chambres") == "chambre"

