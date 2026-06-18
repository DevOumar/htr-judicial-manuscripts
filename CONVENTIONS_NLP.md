# Conventions NLP

## Périmètre

Ce document décrit le post-traitement NLP appliqué après la reconnaissance HTR.
L'entrée est le JSON produit par le pipeline Computer Vision / HTR.

L'objectif n'est pas de produire une édition scientifique définitive. L'objectif
est de produire un jeu de données exploitable en NLP, reproductible, avec texte
normalisé, tokens, lemmes et statistiques.

## Contrat de données

Entrée :

- `dataset_nlp/transcriptions.json`
- schéma : `schemas/transcription_schema.json`

Sortie :

- `dataset_nlp/nlp/transcriptions_enriched.json`
- schéma : `schemas/nlp_schema.json`

Les deux schémas sont validés avec `jsonschema`.

## Règles de normalisation

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
| Tilde nasal | Résoudre certains nasaux explicites | `ã` -> `an`, `õ` -> `on` |
| Graphies fréquentes | Normaliser quelques formes anciennes | `roy` -> `roi`, `reyne` -> `reine` |
| Espaces | Réduire les espaces multiples | `a   b` -> `a b` |

La normalisation globale `u/v` et `i/j` mentionnée dans les consignes NLP n'est
pas appliquée automatiquement. Une règle aveugle peut dégrader les noms propres,
les lieux et les termes juridiques. Elle doit être ajoutée plus tard sous forme
guidée par lexique, après vérification manuelle du corpus.

## Correction guidée par la confiance

Les consignes recommandent d'utiliser `char_confidences` et `candidates`.

État actuel :

- la confiance au niveau ligne est disponible avec `confidence` ;
- le champ `needs_review` est disponible ;
- `char_confidences` n'est pas disponible dans l'export Kraken actuel ;
- les listes de candidats caractère par caractère ne sont pas disponibles.

La correction guidée par candidats est donc documentée mais non appliquée. Le
pipeline utilise `needs_review` pour prioriser la correction manuelle.

## Correction post-HTR par lexique

La correction post-HTR est implementee dans :

```text
src/nlp/correction.py
```

Lexique :

```text
data/lexicons/judicial_lexicon.txt
```

Le pipeline distingue :

- les corrections automatiques appliquees, limitees a des erreurs HTR frequentes
  explicitement listees ;
- les suggestions lexicales, calculees par distance de Levenshtein, mais non
  appliquees automatiquement.

Cette strategie est volontairement prudente. Elle evite de transformer des
graphies anciennes ou des noms propres en formes modernes incorrectes.

## Tokenisation

La tokenisation est implémentée dans :

```text
src/nlp/text_processing.py
```

Elle conserve :

- les tokens mots ;
- les tokens numériques ;
- la ponctuation ;
- les offsets de caractères dans la ligne normalisée.

## Lemmatisation

Le lemmatiseur actuel est conservateur et basé sur des règles. Il traite quelques
formes fréquentes du français ancien sans appliquer de stemming agressif.

Exemples :

| Forme | Lemme |
| --- | --- |
| `roy` | `roi` |
| `reyne` | `reine` |
| `mil` | `mille` |
| `cens` | `cent` |
| `estoit` | `etre` |
| `avoient` | `avoir` |

Ces lemmes servent à l'exploration et au volet NLP. Ils ne doivent pas être
présentés comme une annotation linguistique validée manuellement.

## Évaluation

Sans vérité terrain manuelle, le CER/WER absolu sur le corpus judiciaire ne peut
pas être calculé.

Le projet fournit donc :

- des CER/WER sur CATMuS pour l'évaluation HTR de base ;
- un template de vérité terrain judiciaire ;
- un CSV d'annotation assistée ;
- des statistiques relatives de normalisation et d'EDA.

Les références manuelles doivent être remplies dans :

```text
data/judicial_gt/judicial_gt_annotation.csv
```
