# NLP avance pour la soutenance

Ce module couvre les elements demandes dans les consignes de soutenance qui
depassent la correction post-HTR : NER, BIO, POS, relations, graphe et TEI.

## Commande

```bash
python src/nlp/advanced_pipeline.py --input dataset_nlp/transcriptions.json --lexicon data/lexicons/judicial_lexicon.txt --output-dir dataset_nlp/advanced
```

## Sorties

| Fichier | Role |
| --- | --- |
| `dataset_nlp/advanced/advanced_annotations.json` | Tokens, POS, BIO, entites et relations par ligne |
| `dataset_nlp/advanced/entity_graph.json` | Graphe entites-relations au format JSON |
| `dataset_nlp/advanced/entity_graph.graphml` | Export graphe compatible Gephi/NetworkX |
| `dataset_nlp/advanced/transcription_tei.xml` | Export TEI-XML minimal |
| `dataset_nlp/advanced/advanced_nlp_report.md` | Rapport synthetique |

## Resultats actuels

- Lignes traitees : 247
- Entites detectees : 106
- Relations extraites : 17

Repartition des entites :

- `PER` : 38
- `TITLE` : 26
- `ORG` : 21
- `DATE` : 11
- `LOC` : 10

## Methode

### NER BIO

Le schema BIO utilise :

- `PER` : personnes ou formes capitalisees probables ;
- `LOC` : lieux connus du corpus ;
- `DATE` : mois et annees ;
- `ORG` : institutions ;
- `TITLE` : titres et fonctions.

Exemples :

```text
Roy -> B-TITLE
Paris -> B-LOC
Parlement -> B-ORG
Aoust -> B-DATE
```

### POS

Le POS tagging est heuristique et suit des categories Universal POS simples :

- `NOUN`
- `PROPN`
- `VERB`
- `DET`
- `ADP`
- `CCONJ`
- `NUM`
- `PUNCT`

### Relations

Les relations sont extraites par regles simples :

- `acts_in` : un titre proche d'une institution ;
- `located_near` : une institution proche d'un lieu ;
- `dated` : document ou institution associee a une date ;
- `legal_topic` : mention de concepts juridiques comme `justice moyenne` ou `basse justice`.

## Limites honnetes

Cette implementation est volontairement legere :

- pas de fine-tuning CamemBERT-LoRA termine ;
- pas de POS Stanza/Pie installe ;
- pas de F1 NER fiable faute d'annotations BIO humaines ;
- les relations sont des relations par regles, pas un modele supervise.

Pour la soutenance, il faut presenter cette partie comme une structure
fonctionnelle et reproductible, avec un plan clair pour passer ensuite a un
modele annote et entraine.
