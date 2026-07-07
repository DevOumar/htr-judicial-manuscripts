# Organisation du projet

Ce document distingue les fichiers sources versionnés des artefacts générés localement. L'objectif est de garder le dépôt GitHub lisible pour l'évaluation.

## Dossiers sources versionnés

| Dossier | Rôle |
|---|---|
| `src/preprocessing/` | Prétraitement image : deskew, CLAHE, binarisation Sauvola |
| `src/segmentation/` | Segmentation Kraken, extraction de lignes, PAGE XML |
| `src/htr/` | Baseline et fine-tuning TrOCR |
| `src/evaluation/` | CER/WER, bootstrap, qualité des crops, PAGE XML, benchmark |
| `src/nlp/` | Normalisation, lemmatisation, correction post-HTR |
| `src/export/` | Export JSON/PAGE XML/NLP |
| `src/demo/` | Pipeline judiciaire reproductible |
| `tests/` et `src/tests/` | Tests unitaires et test pipeline |

## Données légères versionnées

| Dossier | Contenu |
|---|---|
| `data/judicial_gt/` | 100 lignes judiciaires annotées et validées |
| `data/lexicons/` | Lexique juridique pour correction post-HTR |
| `dataset_nlp/` | Export NLP léger et reproductible |
| `dataset_nlp/advanced/` | NER/POS rule-based, graphe et TEI-XML |
| `segmentations/` | PAGE XML et polygones légers |
| `schemas/` | Schémas JSON |
| `artifacts/` | Hashes SHA-256 |
| `experiments/` | Journal d'expériences |

## Documentation

| Fichier | Usage |
|---|---|
| `README.md` | Commandes principales et résultats |
| `MODEL_CARD.md` | Fiche du moteur HTR retenu |
| `docs/TECHNICAL_STATUS.md` | État technique final |
| `docs/POST_HTR_CORRECTION.md` | Correction NLP et scores avant/après |
| `docs/JUDICIAL_GROUND_TRUTH.md` | Vérité terrain Parlement de Paris |
| `docs/MD5_COMPLIANCE_REPORT.md` | Conformité aux exigences |
| `docs/FINAL_ARTICLE_DRAFT.md` | Base de rapport final |

## Dossiers générés non versionnés

Ces dossiers restent locaux et sont ignorés par Git :

| Dossier | Raison |
|---|---|
| `outputs/` | Résultats régénérables, images, rapports locaux |
| `models/` | Modèles et checkpoints très lourds |
| `data/raw/` | Images sources téléchargées ou exemples locaux |
| `data/processed/` | Images prétraitées régénérables |
| `__pycache__/`, `.pytest_cache/` | Caches Python/tests |

## Fichiers importants pour la soutenance locale

Les fichiers suivants existent localement après exécution du pipeline :

- `outputs/judicial_demo/page_02_canvas_0022/full_page_transcription_presentation.txt`
- `outputs/nlp_correction/correction_impact_report.md`
- `outputs/judicial_gt_evaluation/final_judicial_evaluation_report.md`
- `outputs/judicial_demo/page_*/page.xml`
- `outputs/judicial_demo/page_*/transcriptions.json`

Ils ne sont pas poussés sur GitHub car ils sont générés et peuvent être recréés avec les commandes du `README.md`.
