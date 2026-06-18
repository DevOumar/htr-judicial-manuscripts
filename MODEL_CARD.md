# Model Card

## Current Final HTR Engine

Current project HTR engine for the judicial demo:

```text
Kraken OCR + ManuMcFrenchV3.mlmodel
```

Model identifier:

```text
10.5281/zenodo.10874058
```

Local model path used during validation:

```text
C:\Users\33767\AppData\Local\htrmopo\htrmopo\34468dee-e4d7-5607-88d3-74a357bf60e8\ManuMcFrenchV3.mlmodel
```

Model family:

- Kraken recognition model;
- trained for French handwritten documents;
- reported by the model registry as a historical French manuscript model, seventeenth to twenty-first centuries;
- license: CC-BY-4.0 according to the Kraken/HTR model metadata.

The previous TrOCR model is retained as a baseline:

```text
models/trocr-catmus-french-decoder/final
```

## Training Data

Primary development corpus:

- `CATMuS/medieval-samples`;
- filtered to French where metadata allows;
- configured split sizes in `config.yaml`:
  - train: 128 lines;
  - validation: 16 lines;
  - test: 16 lines.

Final business corpus:

- Gallica / BnF, Parlement de Paris, manuscript `btv1b9062074w`;
- 5 pages processed;
- 247 Kraken line crops;
- no line-level ground truth yet, template prepared in `data/judicial_gt/`.

## Metrics

### CATMuS TrOCR Baselines

Measured on the small CATMuS French test subset:

| Model | CER | WER |
| --- | ---: | ---: |
| `microsoft/trocr-small-handwritten` | 0.6285 | 0.9722 |
| `models/trocr-catmus-french-decoder/final` | 0.6989 | 0.9722 |
| `dj0w/trocr-french-handwriting-v5` | 1.5896 | 1.5000 |

Bootstrap for the local French decoder:

- CER mean: 0.6989
- CER IC95%: [0.6109, 0.7656]
- WER mean: 0.9722
- WER IC95%: [0.9143, 1.0000]

### Judicial Kraken OCR Run

Measured on 247 Parlement de Paris line crops, without judicial ground truth:

- Lines processed: 247
- Non-empty raw Kraken predictions: 245
- Lines marked `needs_review`: 21
- Mean confidence: 0.9477
- Total runtime: 18.69 s
- Mean runtime: 0.0757 s/line

Example raw predictions:

- `le reply par le Roy la Reyne regenre sa merce`
- `presente, phetippeaux et seeltees du grand seau`
- `mil six cens trente huit, vingt sixiesne mars`

Two very small crops generated empty raw predictions. The final `dataset_nlp` export replaces these empty strings with `[UNK]`, sets `confidence=0.0`, and marks them `needs_review=true` so that PAGE XML and JSON remain valid.

Judicial CER/WER is not reported yet because the manual references in `data/judicial_gt/judicial_gt_template.csv` are intentionally empty. Filling these references is required before a scientific score can be computed.

## Intended Use

Use this model for:

- demonstrating a complete HTR pipeline;
- generating preliminary machine transcriptions;
- prioritizing manual review with `confidence` and `needs_review`;
- baseline comparison before PyLaia/Kraken/further fine-tuning.
- producing the current best automatic transcription available in the project.

Do not use it as a final scholarly transcription model without manual correction.

## Recommended Next Step

Fill `data/judicial_gt/judicial_gt_template.csv` with 100-300 manual references and evaluate Kraken OCR:

```bash
python src/evaluation/evaluate_judicial_gt.py --gt data/judicial_gt/judicial_gt_template.csv --predictions-dir outputs/kraken_ocr_judicial --output outputs/judicial_gt_evaluation/judicial_gt_kraken_metrics.json
```

Then compare:

- PyLaia CATMuS;
- TrOCR Small/Base;
- local TrOCR decoder;
- any additional HTR-United or Kraken historical French model.
