# NLP avancé : NER, POS, relations, graphe et TEI

Cette sortie est une implémentation légère et déterministe pour la soutenance. Elle ne prétend pas remplacer un fine-tuning CamemBERT-LoRA.

- Lignes traitées : 247
- Entités détectées : 106
- Relations extraites : 17

## Entités BIO

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

## Limites honnêtes

- Le NER est fondé sur des règles, pas sur un modèle CamemBERT-LoRA fine-tuné.
- Les étiquettes POS sont produites par des heuristiques de secours, pas par des prédictions Stanza/Pie validées.
- Les relations sont des relations déterministes par proximité ou par règles.
