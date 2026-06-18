# Technical Status

Date: 2026-06-17

## What Works

The complete judicial pipeline is operational:

Gallica -> IIIF download -> preprocessing/resizing -> Kraken segmentation -> line extraction -> Kraken OCR / TrOCR baseline -> PAGE XML -> JSON -> full-page transcription.

Current judicial demo:

- Pages processed: 5
- Extracted lines: 247
- Transcribed lines: 247 in the final export
- Kraken raw non-empty predictions: 245/247
- Final PAGE XML Unicode nodes: 247/247, with `[UNK]` for the two empty raw OCR outputs
- Kraken OCR total transcription time: 18.69 s
- Kraken OCR average transcription time: 0.0757 s/line

Each page contains:

- `original.png`
- `segmentation_input.png`
- `annotated.png`
- `polygons.json`
- `lines/*.png`
- `transcriptions.json`
- `full_page_transcription.txt`
- `page.xml`
- `segmentation_report.json`

Additional Kraken OCR outputs:

- `outputs/kraken_ocr_judicial/kraken_predictions.json`
- `outputs/kraken_ocr_judicial/kraken_predictions.csv`
- `outputs/kraken_ocr_judicial/*/transcriptions_kraken.json`
- `outputs/kraken_ocr_judicial/*/full_page_transcription_kraken.txt`

## NLP Enrichment

Output: `dataset_nlp/nlp/`

The downstream NLP step is now implemented:

- normalized line transcription;
- regex tokenization;
- conservative historical-French lemmatization;
- per-line token and lemma arrays;
- corpus-level lexical statistics.
- deterministic train/validation/test splits;
- SHA-256 hashes for reproducibility.
- lexicon-based post-HTR correction suggestions;
- raw vs corrected vocabulary comparison;
- CER/WER before/after correction evaluation hook.

Latest local run:

- Lines: 247
- Word/number tokens: 1803
- Unique tokens: 923
- Unique lemmas: 897
- Lines marked `needs_review`: 21
- Mean confidence: 0.9477
- NLP split rows: train 171, validation 35, test 41
- NLP test SHA-256: `1b83c6cee55fad98f160b3ce6475c765c7ebbdb54e9642891acce1e04bf1bfe0`
- Correction suggestions: 466
- Automatic cautious corrections applied: 75
- Lines modified by post-HTR correction: 53
- Glued legal terms corrected: `justicemoyenne` -> `justice moyenne`, `bassesustce` -> `basse justice`
- Judicial validated GT lines: 100
- Judicial Kraken CER/WER: 0.1301 / 0.4582
- Post-HTR corrected CER/WER: 0.1075 / 0.4011

Validation:

- `schemas/nlp_schema.json`: valid for `dataset_nlp/nlp/transcriptions_enriched.json`
- Tests include NLP tokenization and lemmatization checks.
- `docs/NLP_REQUIREMENTS_AUDIT.md` maps the NLP PDF requirements to repository artifacts.
- `docs/POST_HTR_CORRECTION.md` documents lexicon correction and before/after impact evaluation.
- `docs/ADVANCED_NLP_PRESENTATION.md` documents rule-based BIO NER, POS, relations, graph export and TEI-XML.
- `src/nlp/ner_training.py` documents the CamemBERT NER scaffold, WordPiece label alignment with `-100`, and seqeval-like F1.
- `data/ner/bio_sample.csv` contains 224 BIO-annotated tokens for the minimal NER training/evaluation sample.
- `outputs/judicial_gt_evaluation/final_judicial_evaluation_report.md` summarizes final CER/WER and bootstrap intervals.

## PAGE XML Validation

Output: `outputs/page_xml_validation_kraken/`

Validated on the 5 judicial pages:

- Valid pages: 5/5
- TextLine count: 247
- Unicode count: 247
- Required `Coords`: present
- Required `Baseline`: present
- Required `TextEquiv/Unicode`: present
- TextLine nesting in TextRegion: valid

The XML is structurally consistent with the PAGE XML namespace used by the project. Full external XSD validation is not included yet.

## Reading Order

Output: `outputs/reading_order/`

Findings:

- Pages analyzed: 5
- Lines analyzed: 247
- Pages with backward y jumps: 5
- Pages likely multicolumn by heuristic: 0

Interpretation: the backward y jumps correspond to the transition from the left column to the right column. The order is compatible with a column-wise reading sequence, but this remains a heuristic validation and should be visually checked using the generated plots.

## Crop Quality

Output: `outputs/crop_analysis/`

Findings:

- Crops analyzed: 247
- Mean width: 411.3 px
- Median width: 456.0 px
- Mean height: 36.5 px
- Median height: 36.0 px
- Mean contrast: 34.9
- Empty-like crops: 0
- Too-small crops: 21
- Possibly truncated crops: 0

Interpretation: segmentation is generally usable. The most visible crop issue is very small marginal or short lines, which can degrade HTR predictions.

## HTR Failure Diagnosis And Rescue

Output: `outputs/htr_analysis/`

Findings:

- Lines analyzed: 247
- Suspicious predictions: 165
- Empty predictions: 0
- Lines with repeated character runs: 122
- Mean prediction length: 24.8 characters

Initial TrOCR diagnosis:

- The current local TrOCR model is not sufficiently adapted to seventeenth-century judicial handwriting.
- Many failures show repeated characters or repeated pseudo-words, for example `lasssss`, `dessssss`, `a man`.
- The domain shift from CATMuS to Parlement de Paris remains large.
- Direct CER/WER cannot be computed on Gallica judicial pages without ground truth.

Rescue action completed:

- A relevant Kraken recognition model was identified and downloaded: `10.5281/zenodo.10874058`, `ManuMcFrenchV3.mlmodel`.
- The project now includes `src/evaluation/predict_kraken_crops.py` to transcribe every extracted line crop with Kraken OCR.
- The final `dataset_nlp/` export uses Kraken predictions through `--htr-source kraken`.
- The qualitative output is substantially more readable than the local TrOCR outputs, although it still requires manual correction for scholarly use.

## Model Benchmark

Output: `outputs/model_benchmark/`

Benchmark constraints:

- Same 3 judicial line crops used for all tested models.
- CPU execution.
- `local_files_only=True`, no network downloads during validation.
- CER/WER reused from prior CATMuS evaluations when available.

| Model | CATMuS CER | CATMuS WER | Judicial avg sec/line | Result |
| --- | ---: | ---: | ---: | --- |
| `microsoft/trocr-small-handwritten` | 0.6285 | 0.9722 | 1.38 | Fast but English-biased output |
| `dj0w/trocr-french-handwriting-v5` | 1.5896 | 1.5000 | 8.80 | More French-looking but too weak/slow here |
| `models/trocr-catmus-french-decoder/final` | 0.6989 | 0.9722 | 1.34 | Local baseline, still poor on judicial pages |
| `microsoft/trocr-base-handwritten` | N/A | N/A | 6.19 | Heavier, English-biased output |
| Kraken `ManuMcFrenchV3.mlmodel` | N/A | N/A | 0.0757 | Best current judicial transcription quality |

Skipped:

- `microsoft/trocr-large-handwritten`: too heavy for routine CPU validation.
- `johnlockejrr/pylaia_catmus_medieval`: not directly exploitable through Transformers/TrOCR in this environment.

Recommendation: keep Kraken `ManuMcFrenchV3.mlmodel` as the current final HTR engine, keep TrOCR as a baseline, and measure true CER/WER once the judicial ground truth file is filled.

## What Does Not Work Well

- Transcriptions are improved and readable in places, but not yet presentation-quality.
- No judicial ground truth exists in the current demo, so final-domain CER/WER is unavailable.
- PAGE XML full XSD validation is not yet implemented.

## What Is Validated

- Full pipeline artifacts exist for 5 pages.
- All 247 extracted lines have final exported transcriptions.
- Full-page transcription files are generated.
- PAGE XML contains all line transcriptions.
- JSON outputs contain all line predictions.
- NLP-enriched JSON contains normalized text, tokens and lemmas.
- Diagnostic reports are generated for PAGE XML, reading order, crops, HTR failures, and model comparison.

## Remaining Improvements

1. Fill judicial line-level ground truth for at least 30-100 lines to measure real CER/WER.
2. Fine-tune on several thousand French historical lines with GPU if Kraken quality remains insufficient after manual evaluation.
3. Compare PyLaia CATMuS and additional HTR-United models when a reliable local inference path is available.
4. Add optional PAGE XML XSD validation.
5. Improve column/reading-order validation with explicit PAGE `ReadingOrder` metadata.
6. Filter or tag very small marginal crops before HTR.

## Final Assessment

The project is technically coherent, reproducible, and suitable for a university demonstration of a complete HTR + downstream NLP pipeline. The engineering pipeline is validated, and the HTR quality has been improved by switching the final judicial transcription from the weak TrOCR baseline to a relevant Kraken French manuscript model. The remaining scientific limitation is the absence of manual judicial ground truth for final CER/WER.
