# NLP avancé pour la soutenance

Ce module couvre les éléments demandés dans les consignes de soutenance qui dépassent la correction post-HTR : NER, BIO, POS, relations, graphe et TEI.

## Commande

```bash
python src/nlp/advanced_pipeline.py --input dataset_nlp/transcriptions.json --lexicon data/lexicons/judicial_lexicon.txt --output-dir dataset_nlp/advanced
```

## Sorties

| Fichier | Rôle |
|---|---|
| `dataset_nlp/advanced/advanced_annotations.json` | Tokens, POS, BIO, entités et relations par ligne |
| `dataset_nlp/advanced/entity_graph.json` | Graphe entités-relations au format JSON |
| `dataset_nlp/advanced/entity_graph.graphml` | Export graphe compatible Gephi/NetworkX |
| `dataset_nlp/advanced/transcription_tei.xml` | Export TEI-XML minimal |
| `dataset_nlp/advanced/advanced_nlp_report.md` | Rapport synthétique |
| `data/ner/bio_sample.csv` | Échantillon BIO de 224 tokens |
| `dataset_nlp/ner/ner_scaffold_report.md` | Scaffold CamemBERT NER, alignement `-100`, F1 type seqeval |

## Résultats actuels

- Lignes traitées : 247
- Entités détectées : 106
- Relations extraites : 17
- Échantillon BIO : 224 tokens

Répartition des entités :

- `PER` : 38
- `TITLE` : 26
- `ORG` : 21
- `DATE` : 11
- `LOC` : 10

## Méthode

### NER BIO

Le schéma BIO utilise :

- `PER` : personnes ou formes capitalisées probables ;
- `LOC` : lieux connus du corpus ;
- `DATE` : mois et années ;
- `ORG` : institutions ;
- `TITLE` : titres et fonctions.

Le fichier `data/ner/bio_sample.csv` contient un échantillon annoté de 224 tokens avec les classes `PER`, `LOC`, `ORG`, `DATE` et `TITLE`.

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
2. pie-extended `medieval-fr` si configuré ;
3. fallback heuristique local.

Le fallback suit des catégories Universal POS simples :

- `NOUN`
- `PROPN`
- `VERB`
- `DET`
- `ADP`
- `CCONJ`
- `NUM`
- `PUNCT`

### Relations

Les relations sont extraites par règles simples :

- `acts_in` : un titre proche d'une institution ;
- `located_near` : une institution proche d'un lieu ;
- `dated` : document ou institution associé à une date ;
- `legal_topic` : mention de concepts juridiques comme `justice moyenne` ou `basse justice`.

## Limites honnêtes

Cette implémentation est volontairement légère :

- pas de fine-tuning CamemBERT-LoRA terminé ;
- POS Stanza/Pie optionnel, fallback local utilisé si les modèles ne sont pas installés ;
- F1 NER uniquement sur le scaffold de contrôle, pas encore sur un vrai split annoté ;
- les relations sont des relations par règles, pas un modèle supervisé.

Pour la soutenance, il faut présenter cette partie comme une structure fonctionnelle et reproductible, avec un plan clair pour passer ensuite à un modèle annoté et entraîné.
