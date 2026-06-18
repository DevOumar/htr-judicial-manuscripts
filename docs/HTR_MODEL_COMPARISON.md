# HTR model comparison

## Objective

Compare the best available HTR starting points before launching a long fine-tuning run.

Models tested:

- `microsoft/trocr-small-handwritten`
- `dj0w/trocr-french-handwriting-v5`
- `models/trocr-catmus-french-decoder/final`
- `johnlockejrr/pylaia_catmus_medieval` checked but not executed

## Test data

### CATMuS French

All TrOCR models were evaluated on the same 4 French CATMuS line images from the configured test split.

### Parlement de Paris

All TrOCR models were also run on the same 5 segmented line crops from the Gallica Parlement de Paris demo.

There is no ground truth transcription for these Gallica lines, so CER/WER cannot be computed for the Parlement set. The comparison is qualitative only.

## CATMuS French quantitative results

| Model | CER | WER | Notes |
| --- | ---: | ---: | --- |
| `microsoft/trocr-small-handwritten` | 0.6285 | 0.9722 | Best measured CER on historical French sample |
| `models/trocr-catmus-french-decoder/final` | 0.6989 | 0.9722 | Local 128-line French decoder-only fine-tune; safer than full fine-tune but worse than baseline CER |
| `dj0w/trocr-french-handwriting-v5` | 1.5896 | 1.5000 | Strong modern French handwriting model, poor transfer to medieval CATMuS sample |

## CATMuS French examples

| Reference | TrOCR small | TrOCR French V5 | Local French decoder |
| --- | --- | --- | --- |
| `uement de lor ames per son exenple. mais a` | `luemeiro belosanes , " Fonevenyle nails a` | `in respectful latest look reflects a resulting Alexander succeeded NewDA taking mis a` | `luement de los enez.e.e.e.e.e..` |
| `trerent molt tost dedens la celle. si esgarde` | `framework would be done to sell a illegal` | `used Global hand redirected conclusion prescription Mr longfP happy civilian Seoul experience 43` | `I mererema motst messt.t.s.s.s.s.` |
| `se leua cil ki mors estoit si prist le main dous` | `to contact humor or your respect to managing` | `games instead new New used once infections giving album Rights do undergraduate killing fewer once killing Stoneest 27` | `totence et limous etrere perssssss` |

## Parlement de Paris qualitative results

Same 5 segmented line crops, no ground truth available.

| Page | TrOCR small | TrOCR French V5 | Local French decoder |
| --- | --- | --- | --- |
| page 01 | `illness .` | `Aouse` | `ilress` |
| page 02 | `whenever` | `Aouse` | `etciones` |
| page 03 | `witness .` | `Aonse` | `etuuse` |
| page 04 | `illnesses .` | `cloust.` | `atssss` |
| page 05 | `thoms .` | `A'ones` | `aess` |

None of these outputs is good enough for final readable judicial transcription.

## PyLaia CATMuS model

`johnlockejrr/pylaia_catmus_medieval` is a relevant historical HTR model trained on CATMuS/medieval. It was not executed in the current pipeline because:

- it is a PyLaia model, not a HuggingFace `VisionEncoderDecoderModel`;
- `pylaia`/`laia` is not installed in the current environment;
- its files are `weights.ckpt`, `syms.txt`, `language_model.*`, etc., not directly consumable by the TrOCR evaluation script.

It remains the best external historical-HRT candidate to test if a PyLaia inference path is added.

## Recommendation

Do not use `dj0w/trocr-french-handwriting-v5` directly for medieval/Judicial Gallica HTR. It is trained for modern French handwriting and performed poorly on the historical CATMuS sample.

Do not rely on the local 128-line fine-tuned model as a final model. It is useful as an experiment, but it does not beat `microsoft/trocr-small-handwritten` on CER.

Best immediate TrOCR starting point:

```text
microsoft/trocr-small-handwritten
```

Best serious next experiment:

```text
Fine-tune TrOCR on the 56,048 French CATMuS lines,
starting from either microsoft/trocr-small-handwritten or dj0w/trocr-french-handwriting-v5,
and keep the checkpoint with the best validation CER.
```

Best non-TrOCR external candidate:

```text
johnlockejrr/pylaia_catmus_medieval
```

This should be evaluated separately with PyLaia before deciding whether TrOCR remains the best architecture for final HTR quality.

