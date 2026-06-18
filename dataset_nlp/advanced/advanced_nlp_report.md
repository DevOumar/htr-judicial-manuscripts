# NLP avance : NER, POS, relations, graphe et TEI

Cette sortie est une implementation legere et deterministe pour la soutenance.
Elle ne pretend pas remplacer un fine-tuning CamemBERT-LoRA.

- Lignes traitees : 247
- Entites detectees : 106
- Relations extraites : 17

## Entites BIO

- `DATE` : 11
- `LOC` : 10
- `ORG` : 21
- `PER` : 38
- `TITLE` : 26

## POS

- `ADP` : 142
- `CCONJ` : 142
- `DET` : 271
- `NOUN` : 1062
- `NUM` : 10
- `PROPN` : 62
- `PUNCT` : 98
- `VERB` : 119

## Sorties

- `annotated_json` : `dataset_nlp\advanced\advanced_annotations.json`
- `graph_json` : `dataset_nlp\advanced\entity_graph.json`
- `graphml` : `dataset_nlp\advanced\entity_graph.graphml`
- `tei` : `dataset_nlp\advanced\transcription_tei.xml`
- `report` : `dataset_nlp\advanced\advanced_nlp_report.md`

## Limites honnetes

- NER is rule-based, not CamemBERT-LoRA fine-tuned.
- POS tags are heuristic fallback tags, not Stanza/Pie predictions.
- Relations are deterministic proximity/rule relations.
