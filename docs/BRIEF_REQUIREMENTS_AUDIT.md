# Audit des exigences du brief

## Objectif

Ce document relie les exigences principales du brief aux fichiers réellement présents dans le dépôt.

## Éléments ajoutés ou consolidés

| Exigence | Statut | Fichiers |
|---|---|---|
| Dataset JSON validé par schéma | Ajouté et généré | `dataset_nlp/transcriptions.json`, `dataset_nlp/metadata.json`, `src/export/export_nlp_dataset.py` |
| PAGE XML et polygones hors sorties volatiles | Ajouté et généré | `segmentations/page_xml/`, `segmentations/polygons/` |
| Dépendances reproductibles | Corrigé | `requirements.txt`, `pyproject.toml` |
| Model card avec métriques et limites | Mis à jour | `MODEL_CARD.md` |
| Test du contrat JSON | Ajouté | `tests/test_data_contract.py` |
| Test de non-régression CER | Ajouté | `tests/test_metrics_regression.py` |
| Outil McNemar | Ajouté | `src/evaluation/mcnemar.py`, `outputs/evaluation/mcnemar_report.json` |
| Structure d'article scientifique | Ajoutée | `docs/FINAL_ARTICLE_DRAFT.md` |
| Enrichissement NLP avec tokens et lemmes | Ajouté et généré | `src/nlp/`, `dataset_nlp/nlp/`, `schemas/nlp_schema.json`, `docs/NLP_PIPELINE.md` |
| EDA NLP, splits et SHA-256 | Ajouté et généré | `src/nlp/eda.py`, `src/nlp/create_splits.py`, `outputs/nlp_eda/`, `artifacts/nlp_dataset_hashes.json` |
| Conventions NLP | Ajouté | `CONVENTIONS_NLP.md`, `docs/NLP_REQUIREMENTS_AUDIT.md` |
| Vérité terrain judiciaire validée | Ajoutée | `data/judicial_gt/judicial_gt_annotation_with_draft.csv` |
| Traçabilité du brief PDF | Ajoutée | `docs/brief/Brief_Projet_Computer_Vision.pdf`, `docs/brief/brief_text.txt` |
| `.gitignore` compatible avec les livrables | Corrigé | `.gitignore` |

## Éléments déjà présents

| Élément | Fichiers |
|---|---|
| Chargement dataset et splits | `src/dataset/load_dataset.py`, `config.yaml` |
| Prétraitement | `src/preprocessing/preprocess.py` |
| Segmentation Kraken | `src/segmentation/kraken_segmentation.py` |
| Polygones et baselines | `outputs/judicial_demo/*/polygons.json`, `segmentations/polygons/` |
| CER/WER | `src/evaluation/evaluate.py`, `src/htr/metrics.py` |
| Bootstrap IC95 % | `src/evaluation/bootstrap.py`, `outputs/evaluation/bootstrap_cer_wer.json` |
| Hash SHA-256 | `artifacts/dataset_hashes.json` |
| Sources et licences | `DATA_SOURCES.md` |

## Livrables finaux

- `README.md`
- `requirements.txt`
- `pyproject.toml`
- `config.yaml`
- `src/`
- `tests/`
- `dataset_nlp/`
- `segmentations/`
- `docs/`
- `experiments/journal.jsonl`
- `MODEL_CARD.md`

## Points importants

1. La lisibilité HTR a été améliorée avec Kraken `ManuMcFrenchV3.mlmodel`, plus adapté aux manuscrits français historiques que le baseline TrOCR.
2. Le CER/WER judiciaire est mesurable grâce au fichier validé `data/judicial_gt/judicial_gt_annotation_with_draft.csv`.
3. L'évaluation repose sur 100 lignes judiciaires validées manuellement.
4. L'IoU est implémenté, mais non calculable sur Gallica sans polygones de référence.

## Commandes de reproduction principales

```bash
python src/evaluation/predict_kraken_crops.py --input-dir outputs/judicial_demo --output-dir outputs/kraken_ocr_judicial --model <chemin_vers_ManuMcFrenchV3.mlmodel>
python src/export/export_nlp_dataset.py --input-dir outputs/judicial_demo --output-dir dataset_nlp --segmentations-dir segmentations --htr-source kraken --kraken-dir outputs/kraken_ocr_judicial
python src/evaluation/validate_data_contract.py --input-dir dataset_nlp/transcriptions.json --schema schemas/transcription_schema.json
python src/nlp/enrich_dataset.py --input dataset_nlp/transcriptions.json --output-dir dataset_nlp/nlp
python src/nlp/eda.py --input dataset_nlp/transcriptions.json --output-dir outputs/nlp_eda
python src/nlp/create_splits.py --input dataset_nlp/transcriptions.json --output-dir dataset_nlp/splits --hash-output artifacts/nlp_dataset_hashes.json --seed 42
python src/evaluation/validate_data_contract.py --input-dir dataset_nlp/nlp/transcriptions_enriched.json --schema schemas/nlp_schema.json
python src/evaluation/page_xml_validation.py --input-dir segmentations/page_xml --output-dir outputs/page_xml_validation_kraken
```

## Résultats synthétiques

- Dataset JSON final : valide.
- PAGE XML : structure validée.
- Vérité terrain judiciaire : 100 lignes validées.
- CER brut : 13,01 %.
- WER brut : 45,82 %.
- CER après correction : 10,75 %.
- WER après correction : 40,11 %.
- Confiance moyenne estimée : 0,9477.
- `needs_review` : environ 8,50 % selon les sorties NLP.
