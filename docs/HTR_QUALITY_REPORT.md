# HTR quality report

## Current model status

The initial `models/trocr-catmus/final` model was not a robust CATMuS model. It was produced by a very small validation run:

- model: `microsoft/trocr-base-handwritten`
- training data: 32 CATMuS lines
- epochs: 1
- steps: 16

It should be treated as a pipeline checkpoint, not as a strong HTR model.

## Experiments

All experiments below were run on CPU. The evaluation sample is intentionally small because generation is slow without GPU, but every model is compared on the same sample for each setting.

### Mixed CATMuS stream

The first streamed rows from `CATMuS/medieval` are mostly Castilian, not French. This explains poor transfer to French judicial registers.

| Model | Training setup | CER | WER |
| --- | --- | ---: | ---: |
| `microsoft/trocr-small-handwritten` | pretrained baseline | 0.8701 | 1.3667 |
| `models/trocr-catmus-light/final` | 128 lines, 1 epoch, low LR | 0.9121 | 1.0000 |
| `models/trocr-catmus-improved/final` | 128 lines, 3 epochs | 0.9162 | 1.9667 |

Result: no reliable CER improvement. Some fine-tuned variants produce more medieval-looking text, but they overfit and repeat common fragments.

### French CATMuS samples

`CATMuS/medieval-samples` contains a usable French subset and is a better proxy for the final Gallica corpus.

| Model | Training setup | CER | WER |
| --- | --- | ---: | ---: |
| `microsoft/trocr-small-handwritten` | pretrained baseline | 0.6285 | 0.9722 |
| `models/trocr-catmus-french/final` | 128 French lines, 3 epochs, full fine-tuning | 0.9135 | 1.0000 |
| `models/trocr-catmus-french-decoder/final` | 128 French lines, 3 epochs, encoder frozen | 0.6989 | 0.9722 |

Result: freezing the encoder is safer than full fine-tuning, but the pretrained baseline still has the best CER on the measured French sample.

## Concrete examples

| Reference | Baseline | Best fine-tuned |
| --- | --- | --- |
| `uement de lor ames per son exenple. mais a` | `luemeiro belosanes , " Fonevenyle nails a` | `luement de los enez.e.e.e.e.e..` |
| `trerent molt tost dedens la celle. si esgarde` | `framework would be done to sell a illegal` | `I mererema motst messt.t.s.s.s.s.` |
| `se leua cil ki mors estoit si prist le main dous` | `to contact humor or your respect to managing` | `totence et limous etrere perssssss` |

The fine-tuned output is more domain-like but still not acceptable as readable HTR.

## Judicial Gallica generalization

The fine-tuned French decoder model was applied to the Gallica judicial demo:

| Page | Kraken lines | Transcribed lines | Example prediction |
| --- | ---: | ---: | --- |
| `page_01_canvas_0021` | 50 | 1 | `ilress` |
| `page_02_canvas_0022` | 48 | 1 | `etciones` |
| `page_03_canvas_0023` | 51 | 1 | `etuuse` |
| `page_04_canvas_0024` | 48 | 1 | `atssss` |
| `page_05_canvas_0025` | 50 | 1 | `aess` |

Result: the segmentation and export pipeline generalizes to the judicial corpus, but the HTR model does not yet produce usable transcriptions on the Parlement de Paris pages.

## Conclusion

The project now has a complete and reproducible HTR pipeline, but the current CPU fine-tuning is not sufficient to improve transcription quality.

The best measured CER remains the pretrained TrOCR small baseline on the French sample:

- baseline CER: 0.6285
- best fine-tuned CER: 0.6989

The best fine-tuned model to keep for experimentation is:

```text
models/trocr-catmus-french-decoder/final
```

It is safer than full fine-tuning, but it should not be presented as a high-quality final HTR model.

## Recommended next step

To obtain genuinely readable judicial transcriptions, the next experiment should be run with:

- a GPU;
- at least several thousand French line images;
- training/validation/test splits from `CATMuS/medieval-samples` filtered to French;
- no full encoder fine-tuning at first;
- CER/WER validation after each epoch;
- manual transcription of 50-100 Parlement de Paris line crops for domain-specific validation.

