from src.nlp.advanced_pipeline import bio_tag_tokens, build_graph, extract_entities, extract_relations
from src.nlp.text_processing import tokenize


def test_bio_pos_entities_and_relations() -> None:
    text = "Le procureur general du Roy a Paris demande justice moyenne"
    tagged = bio_tag_tokens(tokenize(text))
    entities = extract_entities(tagged)
    relations = extract_relations(entities, text.lower())
    graph = build_graph(entities, relations)

    labels = {entity["label"] for entity in entities}
    assert "TITLE" in labels
    assert "LOC" in labels
    assert any(token["pos"] == "VERB" for token in tagged)
    assert any(relation["type"] == "legal_topic" for relation in relations)
    assert graph["nodes"]
    assert graph["edges"]
