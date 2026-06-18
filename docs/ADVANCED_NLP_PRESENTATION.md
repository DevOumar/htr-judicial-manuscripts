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
| `data/ner/bio_sample.csv` | Echantillon BIO de 224 tokens |
| `dataset_nlp/ner/ner_scaffold_report.md` | Scaffold CamemBERT NER, alignement `-100`, F1 type seqeval |

## Resultats actuels

- Lignes traitees : 247
- Entites detectees : 106
- Relations extraites : 17
- Echantillon BIO : 224 tokens

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

Le fichier `data/ner/bio_sample.csv` contient un echantillon annote de 224
tokens avec les classes `PER`, `LOC`, `ORG`, `DATE` et `TITLE`.

Exemples :

```text
Roy -> B-TITLE
Paris -> B-LOC
Parlement -> B-ORG
Aoust -> B-DATE
```

### POS

Le POS tagging passe par `src/nlp/pos_external.py` :

1. Stanza `frm` si disponible ;
2. pie-extended `medieval-fr` si configure ;
3. fallback heuristique local.

Le fallback suit des categories Universal POS simples :

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
- POS Stanza/Pie optionnel, fallback local utilise si les modeles ne sont pas installes ;
- F1 NER uniquement sur le scaffold de controle, pas encore sur un vrai split annote ;
- les relations sont des relations par regles, pas un modele supervise.

Pour la soutenance, il faut presenter cette partie comme une structure
fonctionnelle et reproductible, avec un plan clair pour passer ensuite a un
modele annote et entraine.
