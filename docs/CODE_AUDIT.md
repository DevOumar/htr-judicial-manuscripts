# Code Audit

Date: 2026-06-16

## Scope

This audit covers the repository structure, source modules, generated artifacts, dependencies, and validation outputs used by the current HTR pipeline:

Gallica -> IIIF download -> preprocessing -> Kraken segmentation -> line crops -> TrOCR HTR -> PAGE XML -> JSON -> full-page transcription.

## Current Functional Components

| Component | Status | Main files |
| --- | --- | --- |
| Configuration | Functional | `config.yaml`, `src/utils/config.py` |
| CATMuS dataset loading | Functional | `src/dataset/load_dataset.py`, `src/dataset/visualize.py` |
| TrOCR training/evaluation | Functional | `src/htr/train_trocr.py`, `src/htr/data.py`, `src/htr/metrics.py`, `src/evaluation/evaluate.py` |
| Judicial Gallica demo | Functional | `src/demo/judicial_pipeline.py` |
| Kraken segmentation | Functional | `src/segmentation/kraken_segmentation.py` |
| Line crop transcription | Functional | `src/segmentation/kraken_segmentation.py`, `src/evaluation/predict_line_crops.py` |
| PAGE XML export | Functional inside pipeline | `src/segmentation/kraken_segmentation.py` |
| JSON/full page export | Functional inside pipeline | `src/segmentation/kraken_segmentation.py` |
| PAGE XML validation | Added | `src/evaluation/page_xml_validation.py` |
| Reading order validation | Added | `src/evaluation/reading_order_validation.py` |
| Crop quality analysis | Added | `src/evaluation/crop_quality_analysis.py` |
| HTR failure analysis | Added | `src/evaluation/htr_failure_analysis.py` |
| Model benchmark | Added | `src/evaluation/model_benchmark.py` |
| Full pipeline artifact test | Added | `src/tests/test_full_pipeline.py` |

## Dead Or Obsolete Code

Removed:

- `src/export/export_json.py`: prototype script with hard-coded sample data and side effects on import.
- `src/export/export_pagexml.py`: prototype script generating a minimal sample XML unrelated to the current PAGE XML pipeline.

Removed generated obsolete artifacts:

- `dataset_nlp/output.json`
- `page_xml/sample.xml`
- Python `__pycache__/`
- `.pytest_cache/`

Kept intentionally:

- `outputs/`: ignored by Git, but required for the reproducible judicial validation reports.
- `models/`: ignored by Git, but required to run the current local TrOCR model.
- `data/cache/`: ignored by Git and useful for offline CATMuS work.
- `experiments/journal.jsonl`: currently minimal, but harmless and aligned with earlier experiment tracking work.

## Dependency Audit

Current `requirements.txt` is broadly consistent with the implemented project:

- Required for HTR: `torch`, `torchvision`, `transformers`, `datasets`, `accelerate`, `pillow`, `numpy`, `pandas`, `jiwer`, `editdistance`, `tqdm`, `pyyaml`.
- Required for segmentation/PAGE XML: `kraken`, `lxml`, `requests`.
- Required for image analysis and visualization: `opencv-python`, `scikit-image`, `matplotlib`, `jdeskew`.
- Required for tests: `pytest`.
- Potentially optional: `peft`. It is useful for future efficient fine-tuning, but not required by the current validated pipeline.

No dependency was removed automatically because the project still contains training, evaluation, notebook, and future fine-tuning paths.

## Generated Validation Outputs

| Output | Purpose |
| --- | --- |
| `outputs/page_xml_validation/` | PAGE XML structural validation |
| `outputs/reading_order/` | Reading order plots and report |
| `outputs/crop_analysis/` | Crop size/contrast/problem analysis |
| `outputs/htr_analysis/` | HTR failure diagnosis |
| `outputs/model_benchmark/` | Comparable model runtime/prediction benchmark |

## Main Technical Risks

1. HTR quality remains the principal weakness. The pipeline is complete, but current predictions are not reliably readable.
2. Judicial Gallica pages do not have line-level ground truth, so CER/WER cannot be computed directly on the final business corpus.
3. Reading order is Kraken-derived. The current pages appear two-column; the generated order is mostly column-wise but contains expected column-transition y jumps.
4. TrOCR models are expensive on CPU. Base and historical French models are slower and use more memory.
5. PAGE XML validation checks structural compliance against the generated PAGE namespace and required nodes, but does not perform full XSD validation because the schema file is not bundled locally.

## Cleanup Summary

The repository was cleaned without removing reproducibility-critical artifacts. Prototype export scripts and stale generated files were removed. Runtime outputs remain under ignored directories and are documented as validation artifacts, not source files.

