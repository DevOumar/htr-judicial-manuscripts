# Data Contract

## Status

The final line-level JSON contract is documented and validated by:

- Schema: `schemas/transcription_schema.json`
- Validator: `src/evaluation/validate_data_contract.py`
- Output report: `outputs/data_contract_validation/data_contract_validation_report.json`

The NLP-enriched contract is documented and validated by:

- Schema: `schemas/nlp_schema.json`
- Output: `dataset_nlp/nlp/transcriptions_enriched.json`
- Report: `dataset_nlp/nlp/nlp_report.md`

## Required Fields

Each line object must contain:

| Field | Type | Meaning |
| --- | --- | --- |
| `image_id` | string | Stable image identifier |
| `page_id` | string | Page identifier |
| `line_id` | string | Line identifier |
| `transcription` | string | Final HTR text used by downstream consumers |
| `confidence` | number | Line-level confidence estimate in `[0, 1]` |
| `needs_review` | boolean | Manual review flag |
| `polygon` | array | Text line polygon points |
| `source_image` | string | Source page image used for segmentation |
| `model_name` | string | HTR model used |

The legacy field `prediction` is retained for compatibility and mirrors `transcription`.

## NLP Fields

The NLP-enriched export adds:

| Field | Type | Meaning |
| --- | --- | --- |
| `normalized_transcription` | string | NFC-normalized transcription |
| `rule_normalized_transcription` | string | Transcription after deterministic NLP rules |
| `normalization_rules_applied` | array | Rule names that changed the line |
| `tokens` | array | Token records with offsets |
| `tokens[].text` | string | Surface token |
| `tokens[].normalized` | string | Lowercase normalized token |
| `tokens[].lemma` | string | Conservative historical-French lemma |
| `tokens[].type` | string | `word`, `number`, `punct`, or `unknown` |
| `lemmas` | array | Word/number lemmas for the line |
| `num_tokens` | integer | Token count including punctuation |
| `num_word_tokens` | integer | Word/number token count |

## Validation

```bash
python src/evaluation/quality_flags.py --input-dir outputs/judicial_demo
python src/evaluation/validate_data_contract.py --input-dir outputs/judicial_demo --schema schemas/transcription_schema.json
python src/evaluation/validate_data_contract.py --input-dir dataset_nlp/nlp/transcriptions_enriched.json --schema schemas/nlp_schema.json
```

## Notes

`confidence` is currently an estimated confidence, not a calibrated probability. It uses model token probabilities when available in new pipeline runs and a conservative heuristic for already-generated outputs.
