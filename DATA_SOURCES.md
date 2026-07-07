# Sources de données

## CATMuS Medieval / Medieval Samples

- Usage : corpus de développement et d'évaluation technique HTR.
- Accès : Hugging Face, `CATMuS/medieval-samples`.
- URL : https://huggingface.co/datasets/CATMuS/medieval-samples
- Type : lignes manuscrites avec transcriptions.
- Pertinence : données historiques multilingues, sous-ensemble français exploitable.
- Licence : vérifier la fiche Hugging Face et les métadonnées CATMuS ; usage académique dans ce projet.

## CATMuS Medieval Segmentation

- Usage : validation technique de segmentation pleine page.
- Accès : Hugging Face, `CATMuS/medieval-segmentation`.
- URL : https://huggingface.co/datasets/CATMuS/medieval-segmentation
- Type : pages et objets de mise en page.
- Pertinence : référence géométrique disponible selon les splits et objets exposés.

## HTR-United

- Usage : source candidate pour améliorer le HTR historique français.
- URL : https://htr-united.github.io/
- Type : index de corpus HTR avec images, transcriptions et métadonnées.
- Licence : variable selon le corpus ; vérifier chaque dépôt avant entraînement.

## CREMMA

- Usage : source candidate pour le HTR en ancien français et manuscrits historiques.
- URL : https://cremmalab.github.io/
- Type : corpus et modèles HTR selon disponibilité.
- Licence : variable selon le jeu de données.

## Parlement de Paris / Gallica

- Usage : corpus métier final de démonstration.
- Institution : Bibliothèque nationale de France, Gallica.
- Document : copie de registres du Parlement de Paris, 1643-1644, manuscrit Français 21256.
- URL : https://gallica.bnf.fr/ark:/12148/btv1b9062074w
- Manifeste IIIF : https://gallica.bnf.fr/iiif/ark:/12148/btv1b9062074w/manifest.json
- Type : pages complètes judiciaires manuscrites.
- Licence : conditions d'utilisation Gallica/BnF.
- Pertinence juridique : très forte ; corpus final pour la soutenance.

## Citation recommandée

Le rapport doit citer Gallica/BnF pour les images judiciaires, CATMuS pour les expériences HTR et segmentation, et tout corpus additionnel HTR-United/CREMMA uniquement s'il est effectivement utilisé.
