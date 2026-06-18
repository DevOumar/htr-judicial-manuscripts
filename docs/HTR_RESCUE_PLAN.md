# HTR Rescue Plan

Question: **Comment obtenir une transcription réellement lisible sur les registres judiciaires du Parlement de Paris ?**

Date: 2026-06-17

Update 2026-06-17: a relevant Kraken recognition model has now been tested and integrated:

- model: `ManuMcFrenchV3.mlmodel`
- identifier: `10.5281/zenodo.10874058`
- type: French manuscript Kraken recognition model
- judicial run: 247 line crops processed, 245 raw non-empty predictions
- final export: 247 PAGE XML `Unicode` nodes, using `[UNK]` for two empty tiny-line predictions
- mean confidence: 0.9477
- mean runtime: 0.0757 s/line

This model is currently the best practical HTR engine in the repository. TrOCR remains useful as a baseline, but the final judicial demo should use Kraken OCR.

## Executive Summary

Le pipeline fonctionne, mais aucun modèle testé localement ne produit aujourd'hui une transcription judiciaire lisible. Le problème n'est plus l'orchestration Gallica/Kraken/PAGE XML/JSON; le problème est le modèle de reconnaissance.

Conclusion principale:

1. **Priorite 1: conserver Kraken `ManuMcFrenchV3.mlmodel` comme moteur HTR final actuel.** C'est le meilleur modele directement utilisable trouve pour les registres judiciaires.
2. **Priorite 2: constituer 100 a 300 lignes de ground truth Parlement de Paris.** Sans ground truth judiciaire, il est impossible de mesurer le vrai CER/WER.
3. **Priorite 3: tester PyLaia CATMuS medieval si un chemin d'inference local fiable est disponible.**
4. **Priorite 4: fine-tuning GPU sur CATMuS French + adaptation judiciaire** seulement si Kraken reste insuffisant apres mesure sur verite terrain.

## Current Local Evidence

### CATMuS French Quantitative Benchmark

| Model | CER | WER | Interpretation |
| --- | ---: | ---: | --- |
| `microsoft/trocr-small-handwritten` | 0.6285 | 0.9722 | Best local CER, but English-biased and not readable on judicial pages |
| `models/trocr-catmus-french-decoder/final` | 0.6989 | 0.9722 | Current project model, more historical-looking but unstable |
| `dj0w/trocr-french-handwriting-v5` | 1.5896 | 1.5000 | Modern French model, poor transfer to CATMuS historical sample |

### Judicial Parlement de Paris Qualitative Benchmark

Same crops, no ground truth:

| Model | Example Output | Usable? |
| --- | --- | --- |
| TrOCR Small | `illness .` / English-like phrases | No |
| TrOCR Base | English-like phrases | No |
| `dj0w/trocr-french-handwriting-v5` | More French-looking but still wrong | No |
| Local CATMuS French decoder | `ilress`, `lasssss`, `dessssss` | No |
| Kraken `ManuMcFrenchV3.mlmodel` | `le reply par le Roy la Reyne regenre sa merce`; `mil six cens trente huit` | Best current option |

Local conclusion: **switching directly between TrOCR Small/Base/French V5 does not solve readability**. The direct rescue path that improves the final demo is Kraken OCR with the French manuscript model.

## Candidate Model Audit

### 1. TrOCR Small: `microsoft/trocr-small-handwritten`

Source: Hugging Face model card, Microsoft TrOCR handwritten model: https://huggingface.co/microsoft/trocr-small-handwritten

**Expected performance on historical French:** low to medium. It is robust as a generic handwriting baseline, but it is not trained for early modern French scripts.

**Advantages**

- Already integrated in the project.
- Fastest TrOCR option on CPU.
- Best measured CATMuS French CER among currently tested local models.
- Stable Transformers API.

**Disadvantages**

- English/IAM bias.
- Produces English-looking hallucinations on Parlement crops.
- Not domain-specific.

**Integration difficulty**

- Very low. Already works.

**Compatibility**

- Excellent with current `TrOCRProcessor` and `VisionEncoderDecoderModel`.

**Verdict**

Keep as baseline only. Not sufficient for final readable judicial transcription.

### 2. TrOCR Base: `microsoft/trocr-base-handwritten`

Source: Hugging Face/Microsoft TrOCR family: https://huggingface.co/microsoft/trocr-base-handwritten

**Expected performance on historical French:** not meaningfully better without fine-tuning.

**Advantages**

- Larger capacity than Small.
- Standard Transformers integration.
- Could be a stronger fine-tuning base on GPU.

**Disadvantages**

- Slower and heavier on CPU.
- Local judicial benchmark still produced English-like output.
- No evidence of direct improvement without fine-tuning.

**Integration difficulty**

- Low. Same API as TrOCR Small.

**Compatibility**

- Excellent with current pipeline.

**Verdict**

Use only as a GPU fine-tuning candidate. Do not switch to Base directly for final demo.

### 3. TrOCR Large: `microsoft/trocr-large-handwritten`

Source: Hugging Face/Microsoft TrOCR family: https://huggingface.co/microsoft/trocr-large-handwritten

**Expected performance on historical French:** uncertain. More capacity does not fix domain mismatch by itself.

**Advantages**

- Highest capacity among Microsoft TrOCR baselines.
- Potentially useful if fine-tuned on a large French historical corpus.

**Disadvantages**

- Too heavy for routine CPU experimentation.
- Likely still English/IAM-biased.
- No local benchmark due to CPU cost.

**Integration difficulty**

- Low in code, high in hardware.

**Compatibility**

- API-compatible with current pipeline, but requires GPU for serious use.

**Verdict**

Low priority unless a GPU is available and smaller models have plateaued.

### 4. `dj0w/trocr-french-handwriting-v5`

Source: Hugging Face model card: https://huggingface.co/dj0w/trocr-french-handwriting-v5

**Expected performance on historical French:** low without adaptation. It is French, but modern handwriting is not the same as seventeenth-century judicial hands.

**Advantages**

- French language prior.
- TrOCR-compatible.
- Better than Microsoft models for modern French handwriting.

**Disadvantages**

- Poor local CATMuS historical result.
- Slow on CPU in local benchmark.
- Can still hallucinate modern-looking French.

**Integration difficulty**

- Low. Already tested with existing benchmark code.

**Compatibility**

- Good with current TrOCR pipeline.

**Verdict**

Useful as a fine-tuning starting point, not as a direct final model.

### 5. PyLaia CATMuS: `johnlockejrr/pylaia_catmus_medieval`

Source: Hugging Face model card: https://huggingface.co/johnlockejrr/pylaia_catmus_medieval

**Expected performance on historical French:** high relative to all currently tested models. It is trained on CATMuS medieval, which contains Latin/Romance historical manuscripts and a large French component.

**Advantages**

- Historical manuscript model, not modern handwriting.
- Trained on the most relevant public corpus currently identified.
- Likely stronger than generic TrOCR on historical scripts.

**Disadvantages**

- Not a Transformers TrOCR model.
- Requires PyLaia inference integration.
- Current environment does not have a working PyLaia/Laia inference path.
- Output decoding and image normalization must be matched to the model.

**Integration difficulty**

- Medium to high.

**Compatibility**

- Not directly compatible with current `TrOCRProcessor`.
- Compatible at pipeline level if wrapped as a new HTR backend:
  `line crop -> PyLaia inference -> text -> PAGE XML/JSON`.

**Verdict**

Top external model candidate. This should be tested before launching expensive TrOCR fine-tuning.

### 6. Kraken OCR Recognition

Source: Kraken documentation and project: https://kraken.re/

**Expected performance on historical French:** high when using `ManuMcFrenchV3.mlmodel`, because it is a French manuscript recognition model and is much closer to the Parlement de Paris documents than generic TrOCR.

**Advantages**

- Already installed and integrated for segmentation.
- Designed for historical documents.
- Can serve as a full OCR/HTR engine if a suitable `.mlmodel` is available.
- PAGE XML/ALTO-style workflows are natural for Kraken.

**Disadvantages**

- Not trained specifically on Parlement de Paris.
- Two very small judicial crops still produce empty raw predictions.
- Requires adding a second HTR backend and model-management path.

**Integration difficulty**

- Medium.

**Compatibility**

- Good at pipeline level because line crops already exist.
- Needs backend abstraction:
  `--htr-engine trocr|kraken|pylaia`.

**Verdict**

Use as the current final HTR engine. The project now includes `src/evaluation/predict_kraken_crops.py` and the final NLP export supports `--htr-source kraken`.

### 7. HTR-United Models And Corpora

Source: HTR-United catalog: https://htr-united.github.io/

**Expected performance on historical French:** potentially high if a corpus/model close to chancery, notarial, parliamentary, or administrative French is found.

**Advantages**

- Best discovery hub for historical HTR corpora.
- Can reveal French corpora closer to judicial/administrative sources than CATMuS.
- Useful for both direct model discovery and training data.

**Disadvantages**

- Models are heterogeneous: PyLaia, Kraken, Transkribus exports, custom formats.
- Licenses and image access vary.
- Not one plug-and-play model.

**Integration difficulty**

- Medium to high depending on model format.

**Compatibility**

- Corpus data can be converted to the current line dataset format.
- Model compatibility depends on backend.

**Verdict**

High priority for data/model search, but not a single immediate replacement model.

### 8. HIMANIS / Administrative French Corpora

Sources:

- HIMANIS project: http://himanis.org/
- HTR-United catalog: https://htr-united.github.io/

**Expected performance on Parlement de Paris:** potentially very high as training signal if accessible, because HIMANIS targets French chancery/register material closer to administrative legal writing than generic medieval corpora.

**Advantages**

- Domain closer to legal-administrative French manuscripts.
- Better palaeographic proximity than modern handwriting.
- Strong candidate for pretraining/fine-tuning data.

**Disadvantages**

- Direct ready-to-run model availability must be verified.
- Data formats may require conversion.
- Licensing and image/transcription access must be checked carefully.

**Integration difficulty**

- Medium for data, high for direct model use if not in Transformers/Kraken.

**Compatibility**

- Excellent as training data after conversion to line image + transcription.
- Unknown as direct model.

**Verdict**

Best corpus family to investigate for domain adaptation after PyLaia CATMuS.

### 9. TRIDIS Historical HTR Dataset

Source: Hugging Face dataset: https://huggingface.co/datasets/magistermilitum/Tridis

**Expected performance:** useful as extra training data, not a direct model.

**Advantages**

- Large historical HTR resource.
- Includes French material according to prior project audit.
- May include administrative corpora such as HIMANIS/HOME-like sources.

**Disadvantages**

- Needs filtering by language, period, script and domain.
- Not a direct recognizer.
- Training still requires GPU.

**Integration difficulty**

- Medium.

**Compatibility**

- Good as dataset if normalized into current `image/text/sample_id` format.

**Verdict**

Secondary training source after CATMuS French and any legal-administrative French corpus.

## Strategy For Parlement De Paris

### Step 1: Stop Evaluating Without Ground Truth

Current judicial pages have no reference text. Qualitative inspection is useful, but it cannot guide model selection rigorously.

Minimum required action:

- manually transcribe 100 line crops from `outputs/judicial_demo/page_*/lines/`;
- keep original spelling;
- store as a small judicial validation set;
- compute CER/WER for every candidate model on exactly those lines.

Recommended size:

- 100 lines: quick model triage;
- 300 lines: reliable validation;
- 1,000+ lines: real domain fine-tuning.

### Step 2: Add Backend Abstraction

Current HTR path is TrOCR-only. To rescue quality, the pipeline needs pluggable HTR engines:

```text
line crops
-> HTR backend
   -> TrOCR
   -> PyLaia
   -> Kraken recognition
-> transcriptions.json
-> PAGE XML
```

This is necessary because the most promising historical model is not TrOCR.

### Step 3: Test PyLaia CATMuS On The Same 100 Judicial Lines

Expected value:

- likely better script recognition than TrOCR;
- can validate whether the issue is architecture/data or crop quality.

Decision rule:

- If PyLaia CATMuS clearly improves readability/CER, keep it as the primary HTR backend.
- If it still fails badly, the project needs domain-specific ground truth, not just a different model.

### Step 4: Search HTR-United For Legal/Administrative French

Search criteria:

- French;
- late medieval to early modern;
- chancery, court, notarial, parlement, administrative registers;
- line-level images and transcriptions;
- permissive academic license;
- model format Kraken/PyLaia/Transkribus export if available.

Best expected gain:

- a model or corpus closer to legal-administrative French hands than CATMuS generic medieval samples.

### Step 5: GPU Fine-Tune Only After Candidate Baselines

Do not fine-tune blindly. Fine-tuning should start only after:

- baseline TrOCR Small/Base/French V5 measured on judicial GT;
- PyLaia CATMuS measured on judicial GT;
- any available Kraken/HTR-United model measured on judicial GT.

Recommended first GPU run:

- base: PyLaia CATMuS or TrOCR Base/French V5, depending on benchmark winner;
- data: CATMuS French + any legal French corpus;
- adaptation: add 300-1,000 Parlement lines if possible;
- metric: validation CER on Parlement lines, not only CATMuS.

## Priority Ranking

### Priority 1: Create Judicial Ground Truth

**Why:** without it, model ranking is mostly guesswork.

Effort: low to medium.

Expected impact: very high.

Deliverable:

```text
data/judicial_gt/lines.csv
```

with columns:

```text
page_id,line_id,crop_path,reference
```

### Priority 2: Integrate PyLaia CATMuS Inference

**Why:** best already-trained historical manuscript candidate.

Effort: medium/high.

Expected impact: high.

Decision point:

- If PyLaia beats TrOCR on judicial GT, use PyLaia for final demo.
- If not, proceed to data adaptation.

### Priority 3: Find/Test Kraken Historical Recognition Models

**Why:** Kraken is already used for segmentation and is suitable for historical OCR.

Effort: medium.

Expected impact: medium/high if a relevant model exists, low otherwise.

Decision point:

- Only keep Kraken OCR if it beats TrOCR/PyLaia on judicial GT.

### Priority 4: HTR-United / HIMANIS Corpus Mining

**Why:** likely best source of domain-adjacent French historical data.

Effort: medium/high.

Expected impact: high for fine-tuning.

### Priority 5: GPU Fine-Tune TrOCR Or PyLaia

**Why:** necessary if no off-the-shelf model is readable.

Effort: high.

Expected impact: high only with enough data and validation.

### Priority 6: TrOCR Large

**Why:** more capacity, but not a domain solution.

Effort: high hardware cost.

Expected impact: uncertain.

## Final Recommendation

The most realistic path to readable Parlement de Paris transcription is:

```text
1. Manually transcribe 100-300 judicial line crops.
2. Add PyLaia and Kraken OCR as optional HTR backends.
3. Benchmark TrOCR Small/Base/French V5, PyLaia CATMuS, and any Kraken/HTR-United model on the same judicial GT.
4. Select the best direct model for the demo.
5. If none is readable, run GPU fine-tuning using CATMuS French + legal/administrative French data + Parlement GT.
```

The shortest credible rescue is **PyLaia CATMuS + judicial ground truth evaluation**. The strongest final solution is **domain adaptation with manually transcribed Parlement de Paris lines**.
