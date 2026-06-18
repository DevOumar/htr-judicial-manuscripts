# HTR improvement strategy

## Goal

The project pipeline is validated. The limiting factor is now HTR quality. The objective is to obtain readable transcriptions on French historical manuscripts and then transfer as far as possible to judicial registers from Gallica.

## Best available corpora

| Corpus | URL | Lines | French lines | Period/domain | License | Fit for this project |
| --- | --- | ---: | ---: | --- | --- | --- |
| CATMuS medieval | https://huggingface.co/datasets/CATMuS/medieval | 194,808 | 56,048 verified from Parquet metadata | Medieval historical manuscripts, Romance/Latin, includes French | cc-by-4.0 | Best primary training corpus for historical French HTR |
| CATMuS medieval samples | https://huggingface.co/datasets/CATMuS/medieval-samples | 2,060 | French majority in sample stream; exact full count not required for serious training | Sample subset of CATMuS | dataset card has no explicit license field in local metadata; parent CATMuS is cc-by-4.0 | Good for CPU tests, not enough for final quality |
| TRIDIS | https://huggingface.co/datasets/magistermilitum/Tridis | 197k | French included; exact count not locally verified because remote column scan was too slow | Multilingual historical HTR, includes French examples from HIMANIS/HOME | MIT | Strong secondary corpus, especially if filtered to French/cursive/legal-administrative corpora |
| RIMES-based TrOCR French | https://huggingface.co/dj0w/trocr-french-handwriting-v5 | model, not corpus | modern French handwriting | Modern French handwriting, not historical | MIT | Best TrOCR-compatible pretrained French baseline, but not domain-specific |
| PyLaia CATMuS medieval | https://huggingface.co/johnlockejrr/pylaia_catmus_medieval | model trained on CATMuS/medieval | multilingual historical | Historical Latin/Romance manuscripts | MIT | Best historical pretrained model candidate, but PyLaia not TrOCR |

## CATMuS French estimate

French lines in `CATMuS/medieval` were estimated by reading Parquet metadata for files named `L-Fre.*.parquet`, without downloading image data.

| Split | French lines |
| --- | ---: |
| train | 49,201 |
| dev/validation | 2,712 |
| test | 4,135 |
| total | 56,048 |

By century:

| Century | French lines |
| --- | ---: |
| 12 | 291 |
| 13 | 21,576 |
| 14 | 9,455 |
| 15 | 19,965 |
| 16 | 4,761 |

There is no strong 17th-century French HTR set in CATMuS, but the 15th-16th c. French material is the closest available training signal for the Parlement de Paris demo.

## Existing pretrained models

### TrOCR French Handwriting V5

`dj0w/trocr-french-handwriting-v5` is a TrOCR model fine-tuned from `microsoft/trocr-base-handwritten` on RIMES and custom French handwriting. The model card reports CER 0.20% and WER 1.04% on its validation set, but this is modern French handwriting, not historical judicial script.

Use it as a strong French TrOCR baseline before training from `microsoft/trocr-small-handwritten`.

### PyLaia CATMuS medieval

`johnlockejrr/pylaia_catmus_medieval` is trained on CATMuS/medieval for Latin/Romance historical HTR. It is likely the strongest historical manuscript baseline, but it is not directly TrOCR and requires a PyLaia inference path.

Use it as an external comparator if time allows.

## Why CPU fine-tuning failed

The local experiments used only 128 lines and CPU training. Full fine-tuning quickly overfit and produced repeated fragments. Freezing the encoder was safer but still did not beat the pretrained baseline on CER.

Measured French sample:

| Model | CER | WER |
| --- | ---: | ---: |
| `microsoft/trocr-small-handwritten` | 0.6285 | 0.9722 |
| local French full fine-tuning, 128 lines | 0.9135 | 1.0000 |
| local French decoder-only fine-tuning, 128 lines | 0.6989 | 0.9722 |

Conclusion: CPU experiments are useful for validating code and hyperparameters, not for final quality.

## Serious training plan

Use `config_htr_catmus_french_serious.yaml` on GPU.

Recommended first GPU run:

- corpus: `CATMuS/medieval`, French only;
- train: 10,000 lines;
- validation: 1,000 lines;
- test: 1,000 lines;
- base model: `dj0w/trocr-french-handwriting-v5` first, then compare with `microsoft/trocr-small-handwritten`;
- freeze encoder for the first run;
- LR: `1e-5`;
- epochs: 10 with early stopping;
- batch size: 8, gradient accumulation 2;
- eval/save every 500 steps;
- metrics: CER/WER every epoch/checkpoint;
- keep best checkpoint by validation CER.

Second GPU run:

- unfreeze the last 2-4 encoder layers only;
- keep lower LR (`5e-6` to `1e-5`);
- train on 20k-50k French CATMuS lines if storage allows.

## Expected gains

On CPU:

- realistic gain: small or none;
- goal: verify code, not quality;
- expected CER on historical French: still around 0.6-0.9 on difficult samples.

On GPU with 10k French lines:

- realistic target CER: 0.25-0.45 on CATMuS French validation;
- WER likely remains high on medieval abbreviations but should improve visibly;
- judicial Gallica pages may still be worse because of domain and century shift.

On GPU with 50k French lines plus 50-100 manually transcribed Parlement lines:

- realistic target CER: 0.15-0.30 on similar historical French lines;
- judicial demo should become visibly more readable;
- best result requires domain-specific line ground truth from the Gallica registers.

## Final recommendation

For the final project, use three HTR baselines:

1. `microsoft/trocr-small-handwritten`: generic baseline.
2. `dj0w/trocr-french-handwriting-v5`: best TrOCR-compatible French pretrained baseline.
3. GPU fine-tuned TrOCR on CATMuS French: project model.

If time is short, prioritize evaluating `dj0w/trocr-french-handwriting-v5` on the judicial demo before running a long GPU fine-tune.

