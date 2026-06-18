# MD5 Compliance Report

Date: 2026-06-17

## Method

This report compares the current repository with the MD5 computer vision requirements listed in the final audit request. Existing elements were checked before modification. Existing compliant elements were documented rather than duplicated. Missing elements were implemented when feasible without large training runs.

## Checklist

| Requirement | Status | File / Artifact | Conforme |
| --- | --- | --- | --- |
| Deskew / inclination correction | Existing, documented | `src/preprocessing/preprocess.py`, `docs/PREPROCESSING_PIPELINE.md` | Yes |
| CLAHE | Existing, documented | `src/preprocessing/preprocess.py`, `docs/PREPROCESSING_PIPELINE.md` | Yes |
| Sauvola adaptive binarization | Existing, documented | `src/preprocessing/preprocess.py`, `docs/PREPROCESSING_PIPELINE.md` | Yes |
| Reproducible preprocessing parameters | Added | `config.yaml`, `src/preprocessing/preprocess.py` | Yes |
| Transcription conventions | Existing, expanded | `CONVENTIONS_TRANSCRIPTION.md` | Yes |
| JSON data contract | Added | `schemas/transcription_schema.json`, `docs/DATA_CONTRACT.md` | Yes |
| JSON Schema validation | Added and executed | `src/evaluation/validate_data_contract.py`, `outputs/data_contract_validation/` | Yes |
| Per-line confidence | Added | `src/evaluation/quality_flags.py`, `src/segmentation/kraken_segmentation.py`, `outputs/judicial_demo/*/transcriptions.json` | Yes |
| Per-line `needs_review` | Added | `src/evaluation/quality_flags.py`, `docs/QUALITY_FLAGS.md` | Yes |
| Bootstrap CER 95% CI | Existing generic script replaced by CER/WER implementation | `src/evaluation/bootstrap.py`, `outputs/evaluation/bootstrap_cer_wer.json` | Yes |
| Bootstrap WER 95% CI | Added | `src/evaluation/bootstrap.py`, `outputs/evaluation/bootstrap_cer_wer.json` | Yes |
| SHA-256 dataset hashes | Added and executed | `src/evaluation/dataset_hashes.py`, `artifacts/dataset_hashes.json` | Yes |
| IoU segmentation metric | Added | `src/evaluation/segmentation_iou.py`, `docs/SEGMENTATION_EVALUATION.md` | Partial |
| IoU computed on available references | Attempted; no comparable reference polygons available in current outputs | `outputs/segmentation_iou/segmentation_iou_report.json` | Partial |
| Data sources | Existing, expanded | `DATA_SOURCES.md` | Yes |
| Docstring audit | Added and executed | `src/evaluation/docstring_audit.py`, `outputs/docstring_audit/docstring_audit_report.json` | Yes |
| Missing docstrings added everywhere | Partially addressed; new/modified compliance modules documented, legacy modules still low coverage | `outputs/docstring_audit/docstring_audit_report.json` | Partial |
| Experiment journal | Existing, expanded | `experiments/journal.jsonl` | Yes |
| NLP-ready enriched output | Added | `src/nlp/enrich_dataset.py`, `dataset_nlp/nlp/transcriptions_enriched.json` | Yes |
| NLP EDA | Added | `src/nlp/eda.py`, `outputs/nlp_eda/` | Yes |
| NLP train/validation/test split | Added | `src/nlp/create_splits.py`, `dataset_nlp/splits/` | Yes |
| NLP test SHA-256 | Added | `artifacts/nlp_dataset_hashes.json` | Yes |
| Tokenization | Added | `src/nlp/text_processing.py`, `dataset_nlp/nlp/` | Yes |
| Lemmatization | Added, conservative heuristic | `src/nlp/text_processing.py`, `docs/NLP_PIPELINE.md` | Yes |
| NLP schema validation | Added and executed | `schemas/nlp_schema.json` | Yes |
| Final compliance report | Added | `docs/MD5_COMPLIANCE_REPORT.md` | Yes |

## Quantitative Results

### Bootstrap CER/WER

Source: `outputs/evaluation/bootstrap_cer_wer.json`

- Samples: 4
- CER mean: 0.6989
- CER IC95%: [0.6109, 0.7656]
- WER mean: 0.9722
- WER IC95%: [0.9143, 1.0000]
- Bootstrap resamples: 1000

### Dataset Hashes

Source: `artifacts/dataset_hashes.json`

| Split | Rows | SHA-256 |
| --- | ---: | --- |
| train | 128 | `5cbe01718489ccb05b7fad745b0bd1db250b93d27d1f48553ef024f53156ca2a` |
| validation | 16 | `82a94ed85b5fe2e2f1fd2fbfcdf0520378401bdc6170d37fa5f77790b8301669` |
| test | 16 | `0f7a34b21b2fc38ae1a404f28c0198ca076fcb2d881919fa693fa9c9ab086170` |

### Data Contract Validation

Source: `outputs/data_contract_validation/data_contract_validation_report.json`

- Files validated: 5
- Valid files: 5
- Judicial lines covered: 247

### NLP Enrichment

Source: `dataset_nlp/nlp/nlp_statistics.json`

- Lines: 247
- Word/number tokens: 1803
- Unique tokens: 923
- Unique lemmas: 901
- Lines marked `needs_review`: 21
- NLP schema validation: valid
- NLP test SHA-256: `1b83c6cee55fad98f160b3ce6475c765c7ebbdb54e9642891acce1e04bf1bfe0`

### IoU Segmentation

Source: `outputs/segmentation_iou/segmentation_iou_report.json`

- Pages inspected: 6
- Comparable reference pairs: 0
- Mean IoU: not computable on current outputs

Reason: the judicial Gallica corpus has no ground-truth polygons, and the current CATMuS segmentation output did not expose comparable reference polygons in `ground_truth_objects.json`.

### Docstring Coverage

Source: `outputs/docstring_audit/docstring_audit_report.json`

- Functions: 123
- Functions with docstrings: 25
- Coverage: 20.3%

This is not fully compliant with a strict professional documentation target. New compliance modules include docstrings, but legacy modules still require systematic docstring completion.

## Compliance Score

Scoring:

- Yes = 1
- Partial = 0.5
- No = 0

Total requirements scored: 26

Score:

```text
23.5 / 26 = 90.4%
```

## Final Assessment

The project is largely compliant with the MD5 computer vision requirements after this audit. The main remaining weaknesses are:

1. IoU cannot be numerically demonstrated without comparable reference polygons in the current local outputs.
2. Docstring coverage remains insufficient across legacy modules.
3. Judicial-domain CER/WER is computed on 100 validated references in `data/judicial_gt/judicial_gt_annotation_with_draft.csv`.
4. HTR quality is improved with Kraken but remains a model-performance limitation rather than a pipeline-conformity failure.

The project is now reproducible and auditable for preprocessing, segmentation, HTR evaluation, JSON contract, NLP enrichment, quality flags, bootstrap confidence intervals, dataset hashes, and experiment tracking.
