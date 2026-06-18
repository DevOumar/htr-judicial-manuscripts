# NLP Transcription Dataset

This directory contains the JSON dataset required by the MD5 brief.

- `transcriptions.json`: flat line-level dataset validated by `schemas/transcription_schema.json`.
- `page_*.json`: page-level line datasets.
- `metadata.json`: corpus, source and file metadata.

HTR source: `kraken`.

Important: the current text is machine-generated HTR and must be reviewed for scholarly use. Use `needs_review` and `confidence` to prioritize manual correction. Empty raw predictions are exported as `[UNK]` so that PAGE XML and JSON remain structurally valid.
