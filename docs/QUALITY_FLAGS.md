# Scores de confiance et indicateurs de révision

Le pipeline produit maintenant deux informations de qualité pour chaque ligne :

- `confidence`
- `needs_review`

## Implémentation

Les règles sont implémentées dans :

- `src/evaluation/quality_flags.py`

Elles sont également intégrées aux exports de transcription générés par le pipeline judiciaire.

## Score de confiance

Pour les nouvelles exécutions TrOCR, la confiance peut être estimée à partir de la moyenne des probabilités maximales des tokens générés.

Pour les sorties déjà générées ne contenant pas ces probabilités, le projet utilise une estimation déterministe fondée sur des heuristiques :

- une prédiction vide ou très courte réduit la confiance ;
- des répétitions anormales de caractères réduisent la confiance ;
- des crops très petits réduisent la confiance ;
- un contraste très faible du crop réduit la confiance.

## Indicateur `needs_review`

Une ligne est marquée `needs_review: true` lorsqu'au moins un des cas suivants est détecté :

- confiance inférieure à `0.50` ;
- texte vide ou très court ;
- répétitions suspectes de caractères ;
- crop trop petit ;
- contraste trop faible.

## Limites

Ce score n'est pas une probabilité statistique calibrée. C'est un score pratique de tri pour un pipeline HTR universitaire. Une calibration complète nécessiterait une vérité terrain judiciaire plus large et une analyse de corrélation entre la confiance prédite et le CER observé.
