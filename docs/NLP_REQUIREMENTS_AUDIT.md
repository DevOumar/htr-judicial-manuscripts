# Audit des exigences NLP

Source :

- `docs/brief/Consignes_generales_Projet_NLP.pdf`
- texte extrait : `docs/brief/consignes_nlp_text.txt`

Date : 2026-06-18

## Checklist

| Exigence NLP | Statut | Fichiers |
|---|---|---|
| Ingérer le JSON HTR | Fait | `dataset_nlp/transcriptions.json` |
| Valider le schéma JSON avant le NLP | Fait | `schemas/transcription_schema.json`, `src/evaluation/validate_data_contract.py` |
| EDA : distribution des confiances | Fait | `src/nlp/eda.py`, `outputs/nlp_eda/` |
| EDA : taux `needs_review` | Fait | `src/nlp/eda.py`, `outputs/nlp_eda/` |
| EDA : longueur des lignes | Fait | `src/nlp/eda.py`, `outputs/nlp_eda/` |
| EDA : abréviations résiduelles | Fait | `src/nlp/eda.py`, `outputs/nlp_eda/` |
| Split train/validation/test | Fait | `src/nlp/create_splits.py`, `dataset_nlp/splits/` |
| SHA-256 du test set NLP | Fait | `artifacts/nlp_dataset_hashes.json` |
| Normalisation Unicode NFC | Fait | `src/nlp/normalization.py` |
| Règles d'abréviation avec tilde | Fait | `src/nlp/normalization.py`, `CONVENTIONS_NLP.md` |
| Normalisation u/v et i/j | Reportée | documentée dans `CONVENTIONS_NLP.md`; règle globale jugée risquée |
| Correction guidée par confiance | Non appliquée | bloquée par l'absence de `char_confidences` et `candidates` |
| Tokenisation | Fait | `src/nlp/text_processing.py` |
| Lemmatisation | Fait | `src/nlp/text_processing.py`, `dataset_nlp/nlp/` |
| Lexique de référence | Fait | `data/lexicons/judicial_lexicon.txt` |
| Règles de correction HTR fréquentes | Fait | `src/nlp/correction.py` |
| Suggestions automatiques de correction | Fait | `outputs/nlp_correction/correction_suggestions.csv` |
| Comparaison vocabulaire brut / corrigé | Fait | `outputs/nlp_correction/vocabulary_comparison.md` |
| Distance de Levenshtein | Fait | `src/nlp/correction.py`, `src/htr/metrics.py` |
| Évaluation d'impact avant/après correction | Prête | `outputs/nlp_correction/correction_impact_report.md` |
| Schéma BIO NER | Fait en version rule-based | `src/nlp/advanced_pipeline.py`, `dataset_nlp/advanced/advanced_annotations.json` |
| POS tagging | Fait en version heuristique | `src/nlp/advanced_pipeline.py` |
| Relations simples | Fait | `dataset_nlp/advanced/entity_graph.json` |
| Graphe | Fait | `dataset_nlp/advanced/entity_graph.graphml` |
| TEI-XML | Fait | `dataset_nlp/advanced/transcription_tei.xml` |
| Échantillon BIO 200-300 tokens | Fait | `data/ner/bio_sample.csv` |
| Alignement WordPiece avec `-100` | Fait | `src/nlp/ner_training.py` |
| Évaluation type seqeval | Fait | `src/nlp/ner_training.py`, `dataset_nlp/ner/ner_scaffold_report.md` |
| POS Stanza/Pie | Interface optionnelle + fallback | `src/nlp/pos_external.py` |
| NER avec CamemBERT | Reportée | étape avancée ; échantillon BIO minimal présent, mais pas de fine-tuning complet |
| POS avec Stanza/Pie | Reportée | étape avancée ; modèle externe non installé localement |
| Graphe / TEI | Fait | `dataset_nlp/advanced/` |
| Document de conventions NLP | Fait | `CONVENTIONS_NLP.md` |
| Tests | Fait | `tests/test_data_contract.py`, `tests/test_nlp_pipeline.py`, `tests/test_nlp_normalization.py`, `tests/test_nlp_correction.py` |
| Dépendances reproductibles | Fait | `requirements.txt`, `pyproject.toml` |

## Résultats NLP actuels

- lignes : 247 ;
- tokens mots/nombres : 1803 ;
- formes uniques : 923 ;
- lemmes uniques : 901 ;
- lignes marquées `needs_review` : 21 ;
- suggestions de correction proposées : 466 ;
- corrections appliquées automatiquement : 75 ;
- lignes modifiées par correction : 53 ;
- mots collés corrigés automatiquement : `justicemoyenne` -> `justice moyenne`, `bassesustce` -> `basse justice`.

## Limites honnêtes

1. Le fine-tuning NER CamemBERT nécessiterait un corpus annoté plus large et une phase d'entraînement dédiée.
2. Le POS tagging avec Stanza `frm` ou Pie medieval demande l'installation et la validation de modèles externes.
3. La correction guidée par confiance demande des confiances caractère par caractère et des listes de candidats, absentes de nos exports Kraken actuels.
4. Le CER/WER judiciaire absolu est calculé sur 100 lignes de référence dans `data/judicial_gt/judicial_gt_annotation_with_draft.csv`.
5. Le CER/WER avant/après correction est produit dans `outputs/nlp_correction/correction_impact_report.md`.

Le périmètre robuste réalisé est donc :

```text
JSON HTR -> validation schéma -> EDA -> normalisation déterministe -> tokenisation -> lemmatisation -> correction lexicale -> JSON NLP -> splits + hash
```
