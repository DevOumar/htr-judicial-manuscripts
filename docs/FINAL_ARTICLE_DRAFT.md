# Article Scientifique - Draft

## Resume

Ce projet developpe un pipeline de Computer Vision et HTR pour manuscrits judiciaires francais anciens. A partir de pages Gallica du Parlement de Paris, la chaine telecharge les images IIIF, applique un preprocessing documentaire, segmente les pages avec Kraken, extrait les lignes, transcrit avec TrOCR, puis exporte PAGE XML et JSON valide pour le module NLP. Le pipeline traite 5 pages, 247 lignes et produit un dataset final `dataset_nlp/`. Les experiences HTR montrent que le pipeline est complet mais que la qualite de transcription reste limitee sans ground truth judiciaire specifique.

## Introduction

Les manuscrits judiciaires anciens sont massivement numerises mais restent peu exploitables sans transcription. L'objectif est de transformer des images de pages en donnees textuelles structurees, en conservant les coordonnees des lignes pour la verification et la reutilisation.

## Etat De L'Art

Architectures considerees:

- TrOCR: reconnaissance ligne par ligne via Transformers.
- Kraken: segmentation et OCR/HTR historique.
- PyLaia: modele historique pertinent via CATMuS.
- HTR-United/CATMuS/CREMMA: principaux reservoirs de corpus historiques.

## Donnees

Corpus de developpement:

- CATMuS medieval samples, filtre francais.

Corpus metier:

- Parlement de Paris, Gallica/BnF, manuscrit `btv1b9062074w`, 1643-1644.

Un template de verite terrain judiciaire de 100 lignes est fourni dans `data/judicial_gt/`.

## Methodes

Pipeline:

```text
IIIF -> preprocessing -> Kraken segmentation -> line crops -> TrOCR -> PAGE XML -> JSON -> dataset_nlp
```

Preprocessing:

- deskew;
- CLAHE;
- binarisation Sauvola.

Segmentation:

- Kraken BLLA;
- regions, lignes, baselines, polygones;
- PAGE XML.

HTR:

- baseline TrOCR Small;
- modele local TrOCR decoder fine-tune sur petit subset CATMuS francais;
- comparaison avec TrOCR French V5.

## Resultats

CATMuS French small test:

| Modele | CER | WER |
| --- | ---: | ---: |
| TrOCR Small | 0.6285 | 0.9722 |
| TrOCR local CATMuS decoder | 0.6989 | 0.9722 |
| TrOCR French V5 | 1.5896 | 1.5000 |

Bootstrap modele local:

- CER IC95%: [0.6109, 0.7656]
- WER IC95%: [0.9143, 1.0000]

Pipeline judiciaire:

- 5 pages;
- 247 lignes;
- 247 predictions;
- PAGE XML valide;
- JSON valide.

## Discussion

La segmentation et l'export sont robustes. La limite principale est la reconnaissance HTR: le modele local ne generalise pas suffisamment vers l'ecriture judiciaire du XVIIe siecle. Les prochaines etapes doivent prioriser la constitution d'un ground truth Parlement de Paris et le test de PyLaia CATMuS/Kraken OCR avant tout nouvel entrainement lourd.

## Reproductibilite

Les commandes de reproduction sont dans `README.md`. Les configurations sont dans `config.yaml` et les sorties de validation dans `outputs/`.

## Conclusion

Le projet livre un pipeline complet et auditable du scan brut au JSON NLP. Les transcriptions automatiques sont fonctionnelles mais doivent etre corrigees ou ameliorees par adaptation de domaine pour atteindre un niveau paleographique exploitable.

