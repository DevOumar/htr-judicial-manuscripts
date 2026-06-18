# Conventions NLP

## Périmètre

Ce document décrit le post-traitement NLP appliqué après la reconnaissance HTR.
L'entrée est le JSON produit par le pipeline Computer Vision / HTR.

L'objectif n'est pas de produire une édition scientifique définitive. L'objectif
est de produire un jeu de données exploitable en NLP, reproductible, avec texte
normalisé, tokens, lemmes, entités, relations et exports structurés.

## Contrat de données

Entrée :

- `dataset_nlp/transcriptions.json`
- schéma : `schemas/transcription_schema.json`

Sortie :

- `dataset_nlp/nlp/transcriptions_enriched.json`
- schéma : `schemas/nlp_schema.json`

Les deux schémas sont validés avec `jsonschema`.

## Normalisation

Les règles sont déterministes et implémentées dans :

```text
src/nlp/normalization.py
```

Règles appliquées :

| Règle | Objectif | Exemple |
| --- | --- | --- |
| Unicode NFC | Stabiliser la représentation Unicode | accents décomposés -> accents composés |
| Apostrophes | Harmoniser les apostrophes | `l’ordonnance` -> `l'ordonnance` |
| Abréviations avec tilde | Développer des abréviations fréquentes | `q~` -> `que` |
| Graphies fréquentes | Normaliser quelques formes anciennes | `roy` -> `roi`, `reyne` -> `reine` |
| Espaces | Réduire les espaces multiples | `a   b` -> `a b` |

La normalisation globale `u/v` et `i/j` n'est pas appliquée automatiquement :
elle peut dégrader les noms propres, les lieux et les termes juridiques.

## Correction post-HTR

La correction post-HTR est implémentée dans :

```text
src/nlp/correction.py
```

Elle utilise :

- un lexique juridique : `data/lexicons/judicial_lexicon.txt` ;
- des règles d'erreurs HTR fréquentes ;
- une restauration prudente des mots collés ;
- des suggestions lexicales par distance de Levenshtein.

Exemples :

| HTR brut | Correction |
| --- | --- |
| `justicemoyenne` | `justice moyenne` |
| `bassesustce` | `basse justice` |
| `passeder` | `posseder` |
| `pistice` | `justice` |

## Tokenisation et lemmatisation

La tokenisation est implémentée dans :

```text
src/nlp/text_processing.py
```

Elle conserve :

- les tokens mots ;
- les tokens numériques ;
- la ponctuation ;
- les offsets de caractères.

Le lemmatiseur est conservateur et basé sur des règles. Il traite quelques
formes fréquentes du français ancien sans stemming agressif.

## NER et schéma BIO

Le schéma BIO utilise les classes :

```text
PER, LOC, ORG, DATE, TITLE
```

La classe `TITLE` est ajoutée pour les titres fréquents dans le corpus :
`Roy`, `Seigneur`, `procureur`, `président`, `chancelier`, etc.

Un échantillon minimal de 224 tokens est disponible dans :

```text
data/ner/bio_sample.csv
```

Il sert à valider :

- le format BIO ;
- les classes d'entités ;
- l'alignement avec une tokenisation de type CamemBERT ;
- une évaluation F1 type `seqeval`.

## Alignement WordPiece et `-100`

Le code d'alignement est dans :

```text
src/nlp/ner_training.py
```

Principe :

- le premier sous-token reçoit le label BIO du mot original ;
- les tokens spéciaux reçoivent `-100` ;
- les sous-tokens de continuation reçoivent `-100` pour ne pas contribuer à la loss.

Cette étape est critique pour un futur fine-tuning CamemBERT-LoRA.

## POS et lemmes

Le module optionnel est :

```text
src/nlp/pos_external.py
```

Priorité prévue :

1. Stanza avec modèle `frm`, si installé ;
2. pie-extended `medieval-fr`, si configuré ;
3. fallback local rule-based.

Le fallback permet au dépôt de rester exécutable même sans téléchargement de
modèles externes.

## Relations, graphe et TEI

Le pipeline avancé est dans :

```text
src/nlp/advanced_pipeline.py
```

Il produit :

- `dataset_nlp/advanced/advanced_annotations.json`
- `dataset_nlp/advanced/entity_graph.json`
- `dataset_nlp/advanced/entity_graph.graphml`
- `dataset_nlp/advanced/transcription_tei.xml`

L'export TEI utilise les balises :

- `<persName>` pour `PER` ;
- `<placeName>` pour `LOC` ;
- `<date>` pour `DATE` ;
- `<orgName>` pour `ORG` ;
- `<roleName>` pour `TITLE`.

## Évaluation

Résultats principaux :

- HTR judiciaire brut : CER/WER `0.1301 / 0.4582` ;
- après correction post-HTR : CER/WER `0.1075 / 0.4011` ;
- échantillon BIO : 224 tokens ;
- NER/POS rule-based : 106 entités, 17 relations.

Limite honnête : le fine-tuning CamemBERT-LoRA complet n'est pas lancé. Le dépôt
contient le format, l'alignement, les métriques et les exports nécessaires pour
le faire proprement ensuite.
