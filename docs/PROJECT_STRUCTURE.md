# Organisation du projet

Ce document distingue les fichiers sources versionnes des artefacts generes
localement. L'objectif est de garder le dépôt GitHub lisible pour l'évaluation.

## Dossiers sources versionnes

| Dossier | Role |
| --- | --- |
| `src/preprocessing/` | Pretraitement image : deskew, CLAHE, binarisation Sauvola |
| `src/segmentation/` | Segmentation Kraken, extraction de lignes, PAGE XML |
| `src/htr/` | Baseline et fine-tuning TrOCR |
| `src/evaluation/` | CER/WER, bootstrap, qualité des crops, PAGE XML, benchmark |
| `src/nlp/` | Normalisation, lemmatisation, correction post-HTR |
| `src/export/` | Export JSON/PAGE XML/NLP |
| `src/demo/` | Pipeline judiciaire reproductible |
| `tests/` et `src/tests/` | Tests unitaires et test pipeline |

## Donnees legeres versionnees

| Dossier | Contenu |
| --- | --- |
| `data/judicial_gt/` | 100 lignes judiciaires annotées et validées |
| `data/lexicons/` | Lexique juridique pour correction post-HTR |
| `dataset_nlp/` | Export NLP leger et reproductible |
| `dataset_nlp/advanced/` | NER/POS rule-based, graphe et TEI-XML |
| `segmentations/` | PAGE XML et polygones legers |
| `schemas/` | Schemas JSON |
| `artifacts/` | Hashes SHA-256 |
| `experiments/` | Journal d'experiences |

## Documentation

| Fichier | Usage |
| --- | --- |
| `README.md` | Commandes principales et resultats |
| `docs/TECHNICAL_STATUS.md` | Etat technique final |
| `docs/POST_HTR_CORRECTION.md` | Correction NLP et scores avant/apres |
| `docs/JUDICIAL_GROUND_TRUTH.md` | Verite terrain Parlement de Paris |
| `docs/MD5_COMPLIANCE_REPORT.md` | Conformite aux exigences |
| `docs/FINAL_ARTICLE_DRAFT.md` | Base de rapport final |

## Dossiers generes non versionnes

Ces dossiers restent locaux et sont ignores par Git :

| Dossier | Raison |
| --- | --- |
| `outputs/` | Resultats regenerables, images, rapports locaux |
| `models/` | Modeles et checkpoints tres lourds |
| `data/raw/` | Images sources telechargees ou exemples locaux |
| `data/processed/` | Images preprocessées regenerables |
| `__pycache__/`, `.pytest_cache/` | Caches Python/tests |

## Fichiers importants pour la soutenance locale

Les fichiers suivants existent localement apres execution du pipeline :

- `outputs/judicial_demo/page_02_canvas_0022/full_page_transcription_presentation.txt`
- `outputs/nlp_correction/correction_impact_report.md`
- `outputs/judicial_gt_evaluation/final_judicial_evaluation_report.md`
- `outputs/judicial_demo/page_*/page.xml`
- `outputs/judicial_demo/page_*/transcriptions.json`

Ils ne sont pas pousses sur GitHub car ils sont generes et peuvent etre recréés
avec les commandes du `README.md`.
