# Judicial Ground Truth

## Objective

Create a small Parlement de Paris ground-truth set to measure real CER/WER on the final judicial corpus.

This step does not train any model and does not modify the existing pipeline.

## Generated Files

| File | Purpose |
| --- | --- |
| `data/judicial_gt/judicial_gt_template.csv` | Manual transcription template with 100 selected lines |
| `data/judicial_gt/judicial_gt_annotation_with_draft.csv` | Validated assisted annotation file with Kraken prediction, correction draft, final reference and validation flag |
| `data/judicial_gt/judicial_gt_viewer.html` | Self-contained visual aid for transcription |
| `src/evaluation/create_judicial_gt_template.py` | Deterministic line selection |
| `src/evaluation/create_judicial_gt_annotation_file.py` | Builds the assisted CSV without auto-filling ground truth |
| `src/evaluation/visualize_judicial_gt.py` | HTML viewer generation |
| `src/evaluation/evaluate_judicial_gt.py` | CER/WER evaluation after manual transcription |

## CSV Format

```csv
page_id,line_id,crop_path,reference
```

Only the `reference` column should be filled manually.

The validated assisted file uses:

```csv
page_id,line_id,order,crop_path,prediction,reference_draft,confidence,needs_review,num_corrections,reference,human_validated,notes
```

`reference_draft` is an automatic aid produced from Kraken OCR and post-HTR
correction rules. It is not ground truth. Copy it to `reference` only after
checking the line image manually. Set `human_validated` to `true` when the line
has been checked.

## Selection Method

The template selects 100 lines from the 247 extracted Kraken line crops. The selection is deterministic and aims to cover:

- all 5 pages;
- different positions in reading order;
- regular text lines;
- some difficult low-confidence or review-needed examples;
- no extremely tiny fragments unless needed to reach the target count.

## Manual Transcription Procedure

1. Open:

   ```text
   data/judicial_gt/judicial_gt_viewer.html
   ```

2. Generate the assisted annotation file:

   ```bash
   python src/evaluation/create_judicial_gt_annotation_file.py
   ```

3. For each line crop, enter the manual transcription in:

   ```text
   data/judicial_gt/judicial_gt_annotation_with_draft.csv
   ```

4. Use `reference_draft` only as a suggestion. The final human transcription
   must be written in `reference`.

5. Keep the original spelling as much as possible.

6. Follow:

   ```text
   CONVENTIONS_TRANSCRIPTION.md
   ```

## Evaluation

After filling some or all `reference` values:

```bash
python src/evaluation/evaluate_judicial_gt.py --gt data/judicial_gt/judicial_gt_annotation_with_draft.csv --predictions-dir outputs/judicial_demo
```

Outputs:

- `outputs/judicial_gt_evaluation/judicial_gt_metrics.json`
- `outputs/judicial_gt_evaluation/judicial_gt_predictions.csv`

Rows with an empty `reference` are ignored, so evaluation can start before all 100 lines are transcribed.

Current status:

- selected lines: 100;
- missing predictions in assisted file: 0;
- manual references filled and validated: 100.

## Scientific Use

This ground-truth set enables:

- real CER/WER on Parlement de Paris;
- fair comparison of TrOCR, PyLaia and Kraken OCR on the same lines;
- evidence-based model selection before any new training;
- later domain adaptation if enough manually transcribed lines are accumulated.
