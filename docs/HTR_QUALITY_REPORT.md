# Rapport de qualité HTR

## État du modèle

Les premiers checkpoints TrOCR locaux doivent être considérés comme des checkpoints de validation du pipeline, pas comme des modèles HTR finaux robustes.

Le modèle `models/trocr-catmus/final` provenait d'une très petite expérimentation :

- modèle de base : `microsoft/trocr-base-handwritten` ;
- données : petit échantillon CATMuS ;
- objectif : vérifier que l'entraînement et l'inférence fonctionnaient.

Il ne doit pas être présenté comme un modèle final de haute qualité.

## Constat expérimental

Les expériences CPU avec peu de lignes CATMuS n'ont pas suffi à produire une transcription judiciaire lisible. Les sorties TrOCR présentaient des répétitions et des fragments peu exploitables.

Le passage à Kraken OCR avec un modèle spécialisé en manuscrits français a nettement amélioré la lisibilité.

Modèle final utilisé pour la démonstration judiciaire :

- Kraken OCR ;
- `ManuMcFrenchV3.mlmodel` ;
- modèle spécialisé pour manuscrits français ;
- référence : `10.5281/zenodo.10874058`.

## Résultats judiciaires

Évaluation sur 100 lignes du Parlement de Paris validées manuellement :

| État | CER | WER |
|---|---:|---:|
| HTR brut | 13,01 % | 45,82 % |
| Après correction post-HTR | 10,75 % | 40,11 % |

Ces résultats montrent une amélioration réelle après correction, mais le WER reste élevé. Les erreurs principales concernent :

- mots collés ;
- lettres confondues ;
- graphies anciennes ;
- abréviations ;
- formes absentes des lexiques modernes ;
- erreurs de segmentation ponctuelles.

## Limite principale

Le pipeline est complet et fonctionne. La limite actuelle est la qualité du modèle HTR sur un domaine très spécifique : registres judiciaires français du XVIIe siècle.

## Recommandation

Pour le rendu actuel :

- présenter Kraken comme moteur HTR final ;
- présenter TrOCR comme baseline ;
- indiquer clairement que les corrections NLP améliorent mais ne rendent pas la transcription parfaite ;
- utiliser les scores CER/WER mesurés sur les 100 lignes validées.

Pour améliorer encore :

- augmenter la vérité terrain judiciaire ;
- fine-tuner avec GPU ;
- comparer PyLaia CATMuS et d'autres modèles HTR-United ;
- entraîner ou adapter un modèle sur des lignes proches du Parlement de Paris.
