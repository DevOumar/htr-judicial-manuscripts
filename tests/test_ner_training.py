from src.nlp.ner_training import align_labels_with_wordpieces, bio_entities, load_bio_csv, seqeval_like_scores
from src.nlp.pos_external import tag_with_optional_backend


def test_wordpiece_alignment_masks_continuations_with_minus_100() -> None:
    word_ids = [None, 0, 1, 1, 2, None]
    labels = ["B-PER", "B-LOC", "O"]

    aligned = align_labels_with_wordpieces(word_ids, labels)

    assert aligned[0] == -100
    assert aligned[2] != -100
    assert aligned[3] == -100
    assert aligned[-1] == -100


def test_seqeval_like_scores_exact_entities() -> None:
    refs = [["B-PER", "I-PER", "O", "B-LOC"]]
    preds = [["B-PER", "I-PER", "O", "B-LOC"]]

    scores = seqeval_like_scores(refs, preds)

    assert scores["micro"]["f1"] == 1.0
    assert bio_entities(refs[0]) == {("PER", 0, 2), ("LOC", 3, 4)}


def test_bio_sample_and_pos_fallback_are_available() -> None:
    sample = load_bio_csv()
    tagged = tag_with_optional_backend("Le Roy ordonne a Paris", backend="fallback")

    assert sum(len(row["tokens"]) for row in sample) >= 150
    assert tagged["backend"] == "fallback_rules"
    assert tagged["tokens"]
