# Stratégie d'amélioration HTR

## Constat

Le pipeline complet est validé. Le facteur limitant n'est plus l'orchestration Gallica, Kraken, PAGE XML ou JSON. Le facteur limitant est la qualité de transcription HTR sur les registres judiciaires français anciens.

## Corpus et modèles considérés

| Ressource | Type | Taille / intérêt | Licence | Rôle dans le projet |
|---|---|---:|---|---|
| `CATMuS/medieval` | Dataset HTR historique | 194 808 lignes, dont environ 56 048 lignes françaises estimées | CC-BY-4.0 | Corpus de développement et piste de fine-tuning |
| `CATMuS/medieval-samples` | Sous-échantillon | 2 060 lignes | alignée avec CATMuS | Tests CPU rapides |
| `dj0w/trocr-french-handwriting-v5` | Modèle TrOCR français moderne | modèle, pas corpus | MIT | Baseline française compatible TrOCR |
| `johnlockejrr/pylaia_catmus_medieval` | Modèle PyLaia historique | entraîné sur CATMuS | MIT | Candidat externe très pertinent |
| Kraken `ManuMcFrenchV3.mlmodel` | Modèle Kraken manuscrits français | spécialisé manuscrits français | Zenodo | Moteur final actuel |

## Pourquoi le fine-tuning CPU n'a pas suffi

Les expériences locales ont utilisé de petits échantillons et une exécution CPU. Dans ces conditions, le fine-tuning TrOCR a vite produit des sorties instables ou répétitives. Cela valide le pipeline d'entraînement, mais ne suffit pas à produire un modèle HTR robuste.

Un entraînement sérieux nécessiterait :

- plusieurs milliers de lignes ;
- un GPU ;
- des splits train / validation / test propres ;
- un suivi des checkpoints ;
- une sélection du meilleur modèle sur CER validation.

## Plan d'entraînement sérieux

Si un GPU est disponible, le plan recommandé est :

- corpus : CATMuS français filtré ;
- taille minimale : 10 000 lignes ;
- taille cible : jusqu'à 56 000 lignes françaises ;
- modèle de départ : `dj0w/trocr-french-handwriting-v5` ou `microsoft/trocr-small-handwritten` ;
- epochs : environ 10 avec early stopping ;
- métrique de sélection : CER validation ;
- évaluation finale : test CATMuS + vérité terrain Parlement de Paris.

## Gains attendus

Sur CPU :

- amélioration limitée ;
- utile pour vérifier le code ;
- insuffisant pour une transcription finale de qualité.

Sur GPU avec 10 000 lignes françaises :

- baisse probable du CER sur données proches ;
- meilleure stabilité ;
- gain incertain sur Parlement de Paris si le style d'écriture reste différent.

Sur GPU avec CATMuS français + lignes judiciaires transcrites manuellement :

- meilleure perspective d'adaptation au domaine ;
- gain plus crédible sur les registres judiciaires ;
- besoin d'une vérité terrain judiciaire plus grande.

## Choix actuel

Pour la version actuelle, le meilleur compromis est :

1. utiliser Kraken `ManuMcFrenchV3.mlmodel` comme moteur HTR final ;
2. garder TrOCR comme baseline ;
3. mesurer CER/WER sur les 100 lignes judiciaires validées ;
4. appliquer une correction post-HTR prudente ;
5. documenter CATMuS comme perspective de fine-tuning à grande échelle.

## Conclusion

La voie la plus réaliste pour améliorer fortement la qualité est une adaptation de domaine avec GPU et davantage de vérité terrain judiciaire. Sans GPU, le projet doit privilégier un modèle historique déjà spécialisé, ce qui justifie le choix actuel de Kraken.
