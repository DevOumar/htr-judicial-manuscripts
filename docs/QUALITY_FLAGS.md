# Quality Flags

## Fields

The pipeline now produces:

- `confidence`
- `needs_review`
- `transcription`

Implementation:

- `src/evaluation/quality_flags.py`
- integrated in `src/segmentation/kraken_segmentation.py`

## Confidence Method

For new TrOCR runs, confidence is estimated as the mean maximum token probability returned during generation.

For existing generated outputs where token probabilities were not stored, confidence is estimated with deterministic heuristics:

- empty or very short prediction lowers confidence;
- repeated character runs lower confidence;
- very small crops lower confidence;
- very low crop contrast lowers confidence.

## Needs Review Criteria

A line is marked `needs_review: true` when at least one of the following is true:

- confidence below `0.50`;
- transcription shorter than 3 characters;
- repeated character run such as `ssssss`;
- crop width below 100 px;
- crop height below 18 px;
- crop contrast below 12 grayscale standard deviation.

## Limits

This is not a calibrated statistical confidence. It is a practical triage score for a university HTR pipeline. Proper calibration would require a held-out judicial ground truth set and correlation between confidence and observed CER.
