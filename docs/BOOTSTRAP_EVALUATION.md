# Bootstrap CER/WER

## Status

Bootstrap confidence intervals are implemented in `src/evaluation/bootstrap.py`.

The script computes:

- CER mean;
- WER mean;
- 95 percent bootstrap confidence interval;
- `N=1000` resamples by default.

## Usage

```bash
python src/evaluation/bootstrap.py --predictions outputs/evaluation/french_decoder_predictions.csv --output outputs/evaluation/bootstrap_cer_wer.json --n 1000
```

## Method

The method resamples aligned `(reference, prediction)` pairs with replacement. For each bootstrap sample, CER and WER are recomputed. The 2.5 and 97.5 percentiles form the empirical 95 percent interval.

## Limitation

The current validated evaluation CSV contains only a small CATMuS test subset, so intervals are wide and should not be interpreted as final model performance.
