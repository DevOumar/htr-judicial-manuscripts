# Data Sources

## CATMuS Medieval / Medieval Samples

- Usage: corpus de developpement et d'evaluation technique HTR.
- Acces: Hugging Face, `CATMuS/medieval-samples`.
- URL: https://huggingface.co/datasets/CATMuS/medieval-samples
- Type: lignes manuscrites avec transcriptions.
- Pertinence: donnees historiques multilingues, sous-ensemble francais exploitable.
- Licence: verifier la fiche Hugging Face et les metadonnees CATMuS; usage academique uniquement dans ce projet.

## CATMuS Medieval Segmentation

- Usage: validation technique de segmentation pleine page.
- Acces: Hugging Face, `CATMuS/medieval-segmentation`.
- URL: https://huggingface.co/datasets/CATMuS/medieval-segmentation
- Type: pages et objets de mise en page.
- Pertinence: reference geometrique disponible selon les splits et objets exposes.

## HTR-United

- Usage: source candidate pour ameliorer le HTR historique francais.
- URL: https://htr-united.github.io/
- Type: index de corpus HTR avec images, transcriptions et metadonnees.
- Licence: variable selon corpus; verifier chaque depot avant entrainement.

## CREMMA

- Usage: source candidate pour HTR ancien francais et manuscrits historiques.
- URL: https://cremmalab.github.io/
- Type: corpus et modeles HTR selon disponibilite.
- Licence: variable selon jeu de donnees.

## Parlement De Paris / Gallica

- Usage: corpus metier final de demonstration.
- Institution: Bibliotheque nationale de France, Gallica.
- Document: copie de registres du Parlement de Paris, 1643-1644, manuscrit Francais 21256.
- URL: https://gallica.bnf.fr/ark:/12148/btv1b9062074w
- Manifest IIIF: https://gallica.bnf.fr/iiif/ark:/12148/btv1b9062074w/manifest.json
- Type: pages completes judiciaires manuscrites.
- Licence: conditions d'utilisation Gallica/BnF.
- Pertinence juridique: tres forte; corpus final pour la soutenance.

## Citation Recommandee

Le rapport doit citer Gallica/BnF pour les images judiciaires, CATMuS pour les experiences HTR et segmentation, et tout corpus additionnel HTR-United/CREMMA uniquement s'il est effectivement utilise.
