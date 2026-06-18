# Brief Requirements Audit

Source analyzed:

- `docs/brief/Brief_Projet_Computer_Vision.pdf`
- extracted text: `docs/brief/brief_text.txt`

Date: 2026-06-17

## What Was Missing And Fixed

| Brief requirement | Status after fix | Files |
| --- | --- | --- |
| `dataset_nlp/` JSON dataset validated by schema | Added and generated | `dataset_nlp/transcriptions.json`, `dataset_nlp/metadata.json`, `src/export/export_nlp_dataset.py` |
| PAGE XML / polygon deliverables outside volatile outputs | Added and generated | `segmentations/page_xml/`, `segmentations/polygons/` |
| `requirements.txt` pinned with exact versions | Fixed | `requirements.txt` |
| README reproduction guide | Rewritten | `README.md` |
| MODEL_CARD with metrics, Kraken OCR engine and limitations | Updated | `MODEL_CARD.md` |
| Data contract JSON validation test | Added | `tests/test_data_contract.py` |
| CER non-regression test | Added | `tests/test_metrics_regression.py` |
| McNemar comparison tool | Added | `src/evaluation/mcnemar.py`, `outputs/evaluation/mcnemar_report.json` |
| Scientific article structure | Added as draft | `docs/FINAL_ARTICLE_DRAFT.md` |
| NLP enrichment with tokens and lemmas | Added and generated | `src/nlp/`, `dataset_nlp/nlp/`, `schemas/nlp_schema.json`, `docs/NLP_PIPELINE.md` |
| NLP EDA, splits and SHA-256 | Added and generated | `src/nlp/eda.py`, `src/nlp/create_splits.py`, `outputs/nlp_eda/`, `artifacts/nlp_dataset_hashes.json` |
| NLP conventions from dedicated PDF | Added | `CONVENTIONS_NLP.md`, `docs/NLP_REQUIREMENTS_AUDIT.md` |
| Validated judicial GT annotation file | Added and generated | `data/judicial_gt/judicial_gt_annotation_with_draft.csv`, `src/evaluation/create_judicial_gt_annotation_file.py` |
| PDF brief traceability | Added | `docs/brief/Brief_Projet_Computer_Vision.pdf`, `docs/brief/brief_text.txt` |
| Git ignore compatibility with required deliverables | Fixed | `.gitignore` |

## Already Present Before This Pass

| Brief requirement | Existing files |
| --- | --- |
| Preprocessing: deskew, CLAHE, Sauvola | `src/preprocessing/preprocess.py`, `docs/PREPROCESSING_PIPELINE.md` |
| Dataset loading and splits | `src/dataset/load_dataset.py`, `config.yaml` |
| Kraken page segmentation | `src/segmentation/kraken_segmentation.py` |
| Line polygons and baselines | `outputs/judicial_demo/*/polygons.json`, `segmentations/polygons/` |
| PAGE XML | `outputs/judicial_demo/*/page.xml`, `segmentations/page_xml/` |
| CER/WER | `src/evaluation/evaluate.py`, `src/htr/metrics.py` |
| Bootstrap IC95% | `src/evaluation/bootstrap.py`, `outputs/evaluation/bootstrap_cer_wer.json` |
| SHA-256 dataset hashes | `artifacts/dataset_hashes.json` |
| Transcription conventions | `CONVENTIONS_TRANSCRIPTION.md` |
| Data sources and licenses | `DATA_SOURCES.md` |
| Experiment journal | `experiments/journal.jsonl` |
| Judicial ground truth preparation | `data/judicial_gt/`, `docs/JUDICIAL_GROUND_TRUTH.md` |

## Current Final Deliverables

- `README.md`
- `requirements.txt`
- `src/`
- `tests/`
- `experiments/journal.jsonl`
- `dataset_nlp/`
- `dataset_nlp/nlp/`
- `MODEL_CARD.md`
- `CONVENTIONS_TRANSCRIPTION.md`
- `DATA_SOURCES.md`
- `segmentations/`
- `schemas/transcription_schema.json`
- `docs/`

## Honest Remaining Limitations

1. **HTR readability was improved but still needs manual evaluation.** The final judicial export now uses Kraken `ManuMcFrenchV3.mlmodel`, which is substantially more readable than the TrOCR baseline. This is documented in `MODEL_CARD.md` and `docs/HTR_RESCUE_PLAN.md`.
2. **Judicial CER/WER is now measurable.** The validated file `data/judicial_gt/judicial_gt_annotation_with_draft.csv` contains 100 references and enables scientific CER/WER on Parlement de Paris.
3. **Docstring coverage is not perfect.** New compliance/export modules are documented, but legacy modules remain partially documented.
4. **IoU is implemented but not numerically computable on the judicial corpus** because no reference polygons are provided for Gallica pages.

## Verification Commands

```bash
python src/evaluation/predict_kraken_crops.py --input-dir outputs/judicial_demo --output-dir outputs/kraken_ocr_judicial --model <chemin_vers_ManuMcFrenchV3.mlmodel>
python src/export/export_nlp_dataset.py --input-dir outputs/judicial_demo --output-dir dataset_nlp --segmentations-dir segmentations --htr-source kraken --kraken-dir outputs/kraken_ocr_judicial
python src/evaluation/validate_data_contract.py --input-dir dataset_nlp/transcriptions.json --schema schemas/transcription_schema.json
python src/nlp/enrich_dataset.py --input dataset_nlp/transcriptions.json --output-dir dataset_nlp/nlp
python src/nlp/eda.py --input dataset_nlp/transcriptions.json --output-dir outputs/nlp_eda
python src/nlp/create_splits.py --input dataset_nlp/transcriptions.json --output-dir dataset_nlp/splits --hash-output artifacts/nlp_dataset_hashes.json --seed 42
python src/evaluation/validate_data_contract.py --input-dir dataset_nlp/nlp/transcriptions_enriched.json --schema schemas/nlp_schema.json
python src/evaluation/page_xml_validation.py --input-dir segmentations/page_xml --output-dir outputs/page_xml_validation_kraken
python src/evaluation/mcnemar.py --model-a outputs/evaluation/baseline_french_predictions.csv --model-b outputs/evaluation/french_decoder_predictions.csv
python -m compileall src
python -m pytest
```

Latest local verification:

- PAGE XML: 5/5 valid pages, 247 lines, 247 Unicode nodes.
- JSON data contract: 1/1 final dataset valid.
- Kraken OCR: 247 lines processed, 245 non-empty raw predictions, 21 `needs_review`.
- NLP: 247 lines, 1803 word/number tokens, 901 unique lemmas.
- NLP EDA: mean confidence 0.9477, needs_review 8.50%, residual abbreviation marks 0.
- Tests: 8 passed.
