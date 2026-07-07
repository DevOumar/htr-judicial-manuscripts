# Vérité terrain judiciaire

## Objectif

Créer un petit jeu de vérité terrain Parlement de Paris pour mesurer réellement le CER et le WER sur le corpus judiciaire final.

Cette étape n'entraîne aucun modèle et ne modifie pas le pipeline existant.

## Fichiers

| Fichier | Rôle |
|---|---|
| `data/judicial_gt/judicial_gt_template.csv` | Modèle de transcription manuelle avec 100 lignes sélectionnées |
| `data/judicial_gt/judicial_gt_annotation_with_draft.csv` | Fichier assisté validé, avec prédiction Kraken, proposition corrigée, référence finale et indicateur de validation |
| `src/evaluation/create_judicial_gt_template.py` | Sélection déterministe des lignes |
| `src/evaluation/create_judicial_gt_annotation_file.py` | Création du CSV assisté sans remplir automatiquement la vérité terrain |
| `src/evaluation/visualize_judicial_gt.py` | Génération du visualiseur HTML |
| `src/evaluation/evaluate_judicial_gt.py` | Calcul CER/WER après transcription manuelle |

## Format du CSV

Seule la colonne `reference` doit être remplie manuellement.

```csv
page_id,line_id,order,crop_path,prediction,reference_draft,confidence,needs_review,num_corrections,reference,human_validated,notes
```

`reference_draft` est une aide automatique produite à partir de la sortie Kraken OCR et des corrections post-HTR. Elle ne doit pas être considérée comme une vérité terrain. La référence finale doit être vérifiée sur l'image de ligne. Mettre `human_validated` à `true` lorsque la ligne a été contrôlée.

## Sélection des lignes

Le modèle sélectionne 100 lignes parmi les 247 crops de lignes extraits par Kraken. La sélection est déterministe et vise à couvrir :

- les cinq pages ;
- différentes positions de lecture ;
- des lignes de longueurs variées ;
- quelques exemples difficiles à faible confiance ou marqués `needs_review` ;
- le moins possible de fragments minuscules, sauf si nécessaire pour atteindre 100 lignes.

## Procédure

1. Générer le modèle :

```bash
python src/evaluation/create_judicial_gt_template.py
```

2. Générer le fichier assisté :

```bash
python src/evaluation/create_judicial_gt_annotation_file.py
```

3. Pour chaque crop, saisir la transcription manuelle dans :

```text
data/judicial_gt/judicial_gt_annotation_with_draft.csv
```

4. Conserver autant que possible l'orthographe originale.

5. Marquer `human_validated` à `true` lorsque la ligne est contrôlée.

## Évaluation

```bash
python src/evaluation/evaluate_judicial_gt.py --gt data/judicial_gt/judicial_gt_annotation_with_draft.csv --predictions-dir outputs/judicial_demo
```

Les lignes dont `reference` est vide sont ignorées. L'évaluation peut donc commencer avant que les 100 lignes soient toutes transcrites.

## État actuel

- lignes extraites : 247 ;
- lignes sélectionnées pour vérité terrain : 100 ;
- références manuelles remplies et validées : 100.

Ce fichier permet :

- une mesure réelle du CER/WER sur le corpus Parlement de Paris ;
- une comparaison équitable entre TrOCR, PyLaia et Kraken OCR sur les mêmes lignes ;
- un choix de modèle fondé sur des résultats mesurés avant tout nouvel entraînement.
