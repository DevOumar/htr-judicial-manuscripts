from src.nlp.correction import correct_text, load_lexicon, suggest_token_correction


def test_frequent_htr_correction_rule() -> None:
    lexicon = load_lexicon()
    suggestion = suggest_token_correction("conseit", lexicon)

    assert suggestion["suggestion"] == "conseil"
    assert suggestion["method"] == "frequent_htr_rule"


def test_correct_text_applies_lexicon_suggestion() -> None:
    lexicon = load_lexicon()
    result = correct_text("suivant les arrests de son conseit", lexicon)

    assert "conseil" in result["corrected_text"]
    assert result["num_corrections"] >= 1


def test_correct_text_splits_known_glued_legal_phrase() -> None:
    lexicon = load_lexicon()
    result = correct_text("en tousejusticemoyenne et bassejustice", lexicon)

    assert "toute justice moyenne" in result["corrected_text"]
    assert "basse justice" in result["corrected_text"]
    assert result["num_corrections"] == 2


def test_correct_text_splits_lexicon_words_when_token_is_glued() -> None:
    lexicon = load_lexicon()
    result = correct_text("lettrespatentes du roy", lexicon)

    assert "lettres patentes" in result["corrected_text"]
    assert result["num_corrections"] == 1


def test_correct_text_applies_judicial_htr_error_rules() -> None:
    lexicon = load_lexicon()
    result = correct_text("passeder par lay et bassesustce", lexicon)

    assert result["corrected_text"] == "posseder par luy et basse justice"
