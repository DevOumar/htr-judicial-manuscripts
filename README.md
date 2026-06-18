# HTR Judicial Manuscripts

Pipeline de Computer Vision et HTR pour manuscrits judiciaires francais anciens, applique a des registres du Parlement de Paris disponibles sur Gallica.

Projet MD5 2026, module Vision par ordinateur.

## Objectif

Produire une chaine reproductible:

```text
Gallica / IIIF
-> preprocessing
-> Kraken segmentation
-> extraction des lignes
-> HTR Kraken OCR / TrOCR baseline
-> PAGE XML
-> JSON valide
-> dataset_nlp pour le module NLP
```

## Etat Technique

Fonctionnel:

- chargement CATMuS et splits train/validation/test;
- preprocessing avec deskew, CLAHE et Sauvola;
- segmentation Kraken de pages completes;
- extraction de 247 lignes sur 5 pages judiciaires;
- transcription automatique de toutes les lignes avec Kraken OCR;
- export PAGE XML et JSON;
- export final `dataset_nlp/`;
- enrichissement NLP avec tokenisation, lemmatisation et statistiques lexicales;
- validation JSON Schema;
- evaluation CER/WER et bootstrap;
- corpus de verite terrain judiciaire pret a annoter.

Point HTR actuel:

- le meilleur moteur integre pour la demo judiciaire est Kraken OCR avec le modele francais manuscrit `ManuMcFrenchV3.mlmodel` (`10.5281/zenodo.10874058`);
- TrOCR reste conserve comme baseline et pour les experiences CATMuS;
- le corpus de verite terrain judiciaire contient 100 lignes validees dans `data/judicial_gt/judicial_gt_annotation_with_draft.csv`;
- la correction post-HTR ameliore les scores de `0.1301 / 0.4582` a `0.1075 / 0.4011` en CER/WER sur ce corpus.

## Installation

Prerequis:

- Python 3.10;
- environnement avec assez de RAM pour PyTorch, Transformers et Kraken.

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Reproduire Les Resultats

### 1. Preprocessing

```bash
python src/preprocessing/preprocess.py --config config.yaml --input-dir data/raw --output-dir data/processed
```

### 2. Pipeline judiciaire complet

```bash
python src/demo/judicial_pipeline.py --config config.yaml
```

Sorties principales:

- `outputs/judicial_demo/`
- `outputs/judicial_demo/demo_report.json`

Les fichiers `outputs/judicial_demo/page_*/full_page_transcription.txt`,
`transcriptions.json` et `page.xml` sont synchronises avec Kraken OCR pour la
demo finale.

### 3. HTR Kraken OCR sur les crops judiciaires

Le modele Kraken francais historique se recupere avec:

```bash
set PYTHONUTF8=1
kraken get 10.5281/zenodo.10874058
```

Puis lancer l'OCR Kraken sur toutes les lignes extraites:

```bash
python src/evaluation/predict_kraken_crops.py --input-dir outputs/judicial_demo --output-dir outputs/kraken_ocr_judicial --model <chemin_vers_ManuMcFrenchV3.mlmodel>
```

Sorties principales:

- `outputs/kraken_ocr_judicial/kraken_predictions.json`
- `outputs/kraken_ocr_judicial/kraken_predictions.csv`
- `outputs/kraken_ocr_judicial/*/full_page_transcription_kraken.txt`

Derniere execution locale:

- 247 lignes traitees;
- 245 predictions non vides;
- 21 lignes marquees `needs_review`;
- confiance moyenne: `0.9477`;
- temps moyen: `0.0757 s/ligne`.

### 4. Export NLP final

```bash
python src/export/export_nlp_dataset.py --input-dir outputs/judicial_demo --output-dir dataset_nlp --segmentations-dir segmentations --htr-source kraken --kraken-dir outputs/kraken_ocr_judicial
python src/evaluation/validate_data_contract.py --input-dir dataset_nlp/transcriptions.json --schema schemas/transcription_schema.json
python src/evaluation/page_xml_validation.py --input-dir segmentations/page_xml --output-dir outputs/page_xml_validation_kraken
```

Livrables generes:

- `dataset_nlp/transcriptions.json`
- `dataset_nlp/metadata.json`
- `dataset_nlp/page_*_full_page_transcription.txt`
- `segmentations/page_xml/*.xml`
- `segmentations/polygons/*.json`

### 5. Enrichissement NLP

```bash
python src/nlp/eda.py --input dataset_nlp/transcriptions.json --output-dir outputs/nlp_eda
python src/nlp/create_splits.py --input dataset_nlp/transcriptions.json --output-dir dataset_nlp/splits --hash-output artifacts/nlp_dataset_hashes.json --seed 42
python src/nlp/enrich_dataset.py --input dataset_nlp/transcriptions.json --output-dir dataset_nlp/nlp
python src/nlp/correction.py --input dataset_nlp/transcriptions.json --lexicon data/lexicons/judicial_lexicon.txt --gt data/judicial_gt/judicial_gt_annotation_with_draft.csv --output-dir outputs/nlp_correction
python src/evaluation/validate_data_contract.py --input-dir dataset_nlp/nlp/transcriptions_enriched.json --schema schemas/nlp_schema.json
```

Livrables NLP:

- `dataset_nlp/nlp/transcriptions_enriched.json`
- `dataset_nlp/nlp/page_*_nlp.json`
- `dataset_nlp/nlp/nlp_statistics.json`
- `dataset_nlp/nlp/nlp_report.md`
- `dataset_nlp/nlp/top_tokens.csv`
- `dataset_nlp/nlp/top_lemmas.csv`
- `outputs/nlp_eda/nlp_eda_report.md`
- `dataset_nlp/splits/train.json`
- `dataset_nlp/splits/validation.json`
- `dataset_nlp/splits/test.json`
- `artifacts/nlp_dataset_hashes.json`
- `outputs/nlp_correction/correction_suggestions.csv`
- `outputs/nlp_correction/vocabulary_comparison.md`
- `outputs/nlp_correction/correction_impact_report.md`

Derniere execution locale:

- 247 lignes;
- 1803 tokens mots/nombres;
- 923 formes uniques;
- 897 lemmes uniques;
- 21 lignes `needs_review`.
- confidence moyenne: `0.9477`;
- hash SHA-256 du test NLP: `1b83c6cee55fad98f160b3ce6475c765c7ebbdb54e9642891acce1e04bf1bfe0`.
- suggestions de correction proposees: `466`;
- corrections automatiques prudentes appliquees: `75`.
- CER/WER judiciaire sur 100 lignes validees: `0.1301 / 0.4582`;
- CER/WER apres correction post-HTR: `0.1075 / 0.4011`.

### 6. Evaluation CATMuS

```bash
python src/evaluation/evaluate.py --config config.yaml --model-path models/trocr-catmus-french-decoder/final --split test --output-name french_decoder
python src/evaluation/bootstrap.py --predictions outputs/evaluation/french_decoder_predictions.csv --output outputs/evaluation/bootstrap_cer_wer.json --n 1000
```

Resultats actuels sur le petit test CATMuS francais:

- CER: `0.6989`
- WER: `0.9722`
- Bootstrap CER IC95%: `[0.6109, 0.7656]`
- Bootstrap WER IC95%: `[0.9143, 1.0000]`

### 7. Evaluation judiciaire

Le corpus de verite terrain valide contient 100 lignes:

```bash
data/judicial_gt/judicial_gt_annotation_with_draft.csv
```

Pour regenerer un template vide:

```bash
python src/evaluation/create_judicial_gt_template.py
python src/evaluation/visualize_judicial_gt.py
```

Calculer CER/WER judiciaire:

```bash
python src/evaluation/evaluate_judicial_gt.py --gt data/judicial_gt/judicial_gt_annotation_with_draft.csv --predictions-dir outputs/judicial_demo
```

## Tests

```bash
python -m compileall src
python -m pytest
```

Tests couverts:

- preprocessing;
- coherence des artefacts du pipeline;
- validation du data contract JSON;
- validation du pipeline NLP;
- seuil de non-regression CER quand les artefacts d'evaluation sont presents.

## Structure

```text
src/
  dataset/          chargement CATMuS/Hugging Face
  preprocessing/    deskew, CLAHE, Sauvola
  segmentation/     Kraken, crops, PAGE XML
  htr/              TrOCR training/evaluation helpers
  nlp/              normalisation, tokenisation, lemmatisation
  evaluation/       CER/WER, bootstrap, GT judiciaire, audits
  export/           export dataset_nlp
data/
  judicial_gt/      template manuel Parlement de Paris
dataset_nlp/        JSON final pour le volet NLP
dataset_nlp/nlp/    JSON enrichi, tokens, lemmes, statistiques
segmentations/      PAGE XML et polygones reutilisables
docs/               documentation technique et rapports
experiments/        journal JSONL
schemas/            JSON Schema
```

## Documents Importants

- `docs/TECHNICAL_STATUS.md`
- `docs/MD5_COMPLIANCE_REPORT.md`
- `docs/HTR_RESCUE_PLAN.md`
- `docs/JUDICIAL_GROUND_TRUTH.md`
- `docs/NLP_PIPELINE.md`
- `docs/NLP_REQUIREMENTS_AUDIT.md`
- `docs/POST_HTR_CORRECTION.md`
- `docs/DATA_CONTRACT.md`
- `CONVENTIONS_NLP.md`
- `CONVENTIONS_TRANSCRIPTION.md`
- `DATA_SOURCES.md`
- `MODEL_CARD.md`

## Donnees Et Licences

- CATMuS: corpus de developpement HTR.
- Gallica/BnF: corpus judiciaire final, `btv1b9062074w`.
- Les conditions de licence et d'attribution sont documentees dans `DATA_SOURCES.md`.
