# Fiche modèle

## Moteur HTR final actuel

Le moteur HTR final utilisé pour la démonstration judiciaire est :

```text
Kraken OCR + ManuMcFrenchV3.mlmodel
```

Identifiant du modèle :

```text
10.5281/zenodo.10874058
```

Chemin local utilisé pendant la validation :

```text
C:\Users\33767\AppData\Local\htrmopo\htrmopo\34468dee-e4d7-5607-88d3-74a357bf60e8\ManuMcFrenchV3.mlmodel
```

Famille du modèle :

- modèle de reconnaissance Kraken ;
- entraîné pour des documents manuscrits français ;
- indiqué dans le registre de modèles comme modèle pour manuscrits français historiques, du XVIIe au XXIe siècle ;
- licence : CC-BY-4.0 d'après les métadonnées Kraken/HTR.

Le modèle TrOCR précédent est conservé comme baseline :

```text
models/trocr-catmus-french-decoder/final
```

## Données

### Corpus de développement

Le corpus CATMuS est utilisé comme ressource de développement et comme piste de fine-tuning futur :

- `CATMuS/medieval` ;
- `CATMuS/medieval-samples` pour les tests légers ;
- filtrage vers le français lorsque les métadonnées le permettent ;
- environ 56 000 lignes françaises exploitables identifiées comme potentiel d'entraînement à grande échelle.

Important : aucun entraînement massif sur ces 56 000 lignes n'a été lancé dans la version finale du projet.

### Corpus métier final

Le corpus final est le corpus judiciaire :

- Gallica / BnF ;
- registres du Parlement de Paris ;
- manuscrit `btv1b9062074w` ;
- période : 1643-1644 ;
- 5 pages traitées ;
- 247 crops de lignes produits par Kraken ;
- 100 lignes validées manuellement dans `data/judicial_gt/judicial_gt_annotation_with_draft.csv`.

## Métriques

### Baselines TrOCR sur CATMuS

Résultats mesurés sur un petit sous-ensemble CATMuS français :

| Modèle | CER | WER |
|---|---:|---:|
| `microsoft/trocr-small-handwritten` | 0,6285 | 0,9722 |
| `models/trocr-catmus-french-decoder/final` | 0,6989 | 0,9722 |
| `dj0w/trocr-french-handwriting-v5` | 1,5896 | 1,5000 |

Ces scores servent au positionnement des baselines. Ils ne sont pas les scores finaux du corpus judiciaire.

### Exécution Kraken OCR sur le corpus judiciaire

Mesures sur les 247 lignes du Parlement de Paris :

- lignes traitées : 247 ;
- prédictions Kraken non vides : 245 ;
- lignes marquées `needs_review` : 21 ;
- confiance moyenne estimée : 0,9477 ;
- temps total : 18,69 s ;
- temps moyen : 0,0757 s/ligne.

Exemples de prédictions brutes :

- `le reply par le Roy la Reyne regenre sa merce`
- `presente, phetippeaux et seeltees du grand seau`
- `mil six cens trente huit, vingt sixiesne mars`

Deux crops très petits ont produit une prédiction brute vide. L'export final `dataset_nlp` remplace ces chaînes vides par `[UNK]`, définit `confidence=0.0` et marque `needs_review=true` afin de garder les fichiers PAGE XML et JSON valides.

### Scores finaux sur la vérité terrain judiciaire

Les scores suivants sont calculés sur les 100 lignes judiciaires validées manuellement :

| Système | CER | WER |
|---|---:|---:|
| Kraken OCR brut | 13,01 % | 45,82 % |
| Kraken OCR + correction post-HTR | 10,75 % | 40,11 % |

Intervalles de confiance bootstrap à 95 % :

| Système | CER IC95 | WER IC95 |
|---|---|---|
| Kraken OCR brut | [11,96 %, 14,19 %] | [42,22 %, 49,58 %] |
| Kraken OCR + correction post-HTR | [9,62 %, 12,05 %] | [36,34 %, 44,10 %] |

## Usage prévu

Ce modèle est utilisé pour :

- démontrer un pipeline HTR complet ;
- produire des transcriptions automatiques préliminaires ;
- transcrire les lignes extraites des pages judiciaires ;
- générer des exports PAGE XML et JSON exploitables ;
- prioriser la relecture manuelle avec `confidence` et `needs_review` ;
- fournir le meilleur moteur HTR automatique actuellement intégré au projet.

Il ne doit pas être utilisé comme transcription scientifique définitive sans correction humaine.

## Limites

- Les transcriptions restent imparfaites.
- Le WER reste élevé à cause des mots collés, des graphies anciennes, des abréviations et des confusions de lettres.
- Le modèle n'a pas été fine-tuné spécifiquement sur un grand corpus Parlement de Paris.
- Les scores sont calculés sur 100 lignes validées, ce qui est suffisant pour une évaluation de projet mais reste limité pour une publication scientifique complète.

## Prochaines étapes recommandées

1. Étendre la vérité terrain judiciaire au-delà de 100 lignes.
2. Tester PyLaia CATMuS sur les mêmes lignes.
3. Comparer d'autres modèles HTR-United ou Kraken spécialisés.
4. Lancer un fine-tuning GPU sur CATMuS français et sur des lignes judiciaires validées.
5. Sélectionner le meilleur modèle sur CER validation, puis mesurer CER/WER final sur un test judiciaire séparé.
