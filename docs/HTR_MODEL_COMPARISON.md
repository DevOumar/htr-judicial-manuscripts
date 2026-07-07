# Comparaison des modèles HTR

## Objectif

Comparer les moteurs HTR envisagés pour transcrire les registres judiciaires du Parlement de Paris.

## Modèles étudiés

| Modèle | Type | Avantages | Limites | Décision |
|---|---|---|---|---|
| `microsoft/trocr-small-handwritten` | TrOCR générique | Facile à intégrer, rapide | Entraîné surtout sur écriture moderne anglophone | Baseline |
| `microsoft/trocr-base-handwritten` | TrOCR générique plus lourd | Plus grande capacité | Lent sur CPU, pas spécialisé ancien français | Baseline secondaire |
| `dj0w/trocr-french-handwriting-v5` | TrOCR français moderne | Français, compatible Hugging Face | Écriture moderne, transfert faible vers manuscrits judiciaires anciens | Point de départ possible, pas final |
| `johnlockejrr/pylaia_catmus_medieval` | PyLaia historique | Entraîné sur CATMuS, domaine historique | Pas compatible directement avec TrOCRProcessor | Candidat futur sérieux |
| Kraken `ManuMcFrenchV3.mlmodel` | Kraken OCR historique français | Spécialisé manuscrits français, intégré au pipeline | Nécessite backend Kraken | Moteur final actuel |

## Résultat principal

Les modèles TrOCR testés localement ne suffisent pas à obtenir une transcription judiciaire lisible sans fine-tuning sérieux. Le meilleur choix pratique pour la démonstration actuelle est Kraken OCR avec `ManuMcFrenchV3.mlmodel`.

## Évaluation judiciaire

L'évaluation finale repose sur les mêmes 100 lignes judiciaires validées manuellement.

| Système | CER | WER |
|---|---:|---:|
| Kraken brut | 13,01 % | 45,82 % |
| Kraken + correction post-HTR | 10,75 % | 40,11 % |

## PyLaia CATMuS

Le modèle `johnlockejrr/pylaia_catmus_medieval` reste très pertinent car il est entraîné sur CATMuS/medieval. Il n'a pas été intégré comme moteur final car :

- ce n'est pas un modèle Hugging Face `VisionEncoderDecoderModel` ;
- les fichiers sont au format PyLaia ;
- il faut ajouter un backend d'inférence séparé ;
- la normalisation image et le décodage doivent correspondre au modèle.

## Recommandation

Pour la version actuelle :

1. garder Kraken `ManuMcFrenchV3.mlmodel` comme moteur HTR final ;
2. garder TrOCR comme baseline ;
3. ne pas présenter le petit fine-tuning TrOCR local comme modèle final ;
4. utiliser CATMuS comme perspective de fine-tuning à grande échelle ;
5. tester PyLaia CATMuS si le temps permet d'ajouter un backend propre.
