# Audit des exigences NLP

Source :

- `docs/brief/Consignes_generales_Projet_NLP.pdf`
- texte extrait : `docs/brief/consignes_nlp_text.txt`

Date : 2026-06-18

## Checklist

| Exigence NLP | Statut | Fichiers |
| --- | --- | --- |
| Ingerer le JSON HTR | Fait | `dataset_nlp/transcriptions.json` |
| Valider le schema JSON avant le NLP | Fait | `schemas/transcription_schema.json`, `src/evaluation/validate_data_contract.py` |
| EDA : distribution des confiances | Fait | `src/nlp/eda.py`, `outputs/nlp_eda/` |
| EDA : taux `needs_review` | Fait | `src/nlp/eda.py`, `outputs/nlp_eda/` |
| EDA : longueur des lignes | Fait | `src/nlp/eda.py`, `outputs/nlp_eda/` |
| EDA : abreviations residuelles | Fait | `src/nlp/eda.py`, `outputs/nlp_eda/` |
| Split train/validation/test | Fait | `src/nlp/create_splits.py`, `dataset_nlp/splits/` |
| SHA-256 du test set NLP | Fait | `artifacts/nlp_dataset_hashes.json` |
| Normalisation Unicode NFC | Fait | `src/nlp/normalization.py` |
| Regles d'abreviation avec tilde | Fait | `src/nlp/normalization.py`, `CONVENTIONS_NLP.md` |
| Normalisation u/v et i/j | Reportee | documentee dans `CONVENTIONS_NLP.md`; regle globale jugee risquee |
| Correction guidee par confiance | Non appliquee | bloquee par l'absence de `char_confidences` et `candidates` |
| Tokenisation | Fait | `src/nlp/text_processing.py` |
| Lemmatisation | Fait | `src/nlp/text_processing.py`, `dataset_nlp/nlp/` |
| Lexique de reference | Fait | `data/lexicons/judicial_lexicon.txt` |
| Regles de correction HTR frequentes | Fait | `src/nlp/correction.py` |
| Suggestions automatiques de correction | Fait | `outputs/nlp_correction/correction_suggestions.csv` |
| Comparaison vocabulaire brut / corrige | Fait | `outputs/nlp_correction/vocabulary_comparison.md` |
| Distance de Levenshtein | Fait | `src/nlp/correction.py`, `src/htr/metrics.py` |
| Evaluation d'impact avant/apres correction | Prete | `outputs/nlp_correction/correction_impact_report.md` |
| NER avec CamemBERT | Reportee | etape avancee ; il manque 200-300 tokens annotes |
| POS avec Stanza/Pie | Reportee | etape avancee ; modele externe non installe |
| Graphe / TEI | Reportee | etape avancee |
| Document de conventions NLP | Fait | `CONVENTIONS_NLP.md` |
| Tests | Fait | `tests/test_data_contract.py`, `tests/test_nlp_pipeline.py`, `tests/test_nlp_normalization.py`, `tests/test_nlp_correction.py` |
| Dependances reproductibles | Fait | `requirements.txt`, `pyproject.toml` |

## Resultats NLP actuels

- lignes : 247 ;
- tokens mots/nombres : 1803 ;
- formes uniques : 923 ;
- lemmes uniques : 901 ;
- lignes marquees `needs_review` : 21 ;
- suggestions de correction proposees : 466 ;
- corrections appliquees automatiquement : 75 ;
- lignes modifiees par correction : 53 ;
- mots colles corriges automatiquement : `justicemoyenne` -> `justice moyenne`, `bassesustce` -> `basse justice`.

## Limites honnetes

1. Le fine-tuning NER CamemBERT necessite 200-300 tokens annotes manuellement.
2. Le POS tagging avec Stanza `frm` ou Pie medieval demande l'installation et la validation de modeles externes.
3. La correction guidee par confiance demande des confiances caractere par caractere et des listes de candidats, absentes de nos exports Kraken actuels.
4. Le CER/WER judiciaire absolu est calcule sur 100 lignes de reference dans `data/judicial_gt/judicial_gt_annotation_with_draft.csv`.
5. Le CER/WER avant/apres correction est produit dans `outputs/nlp_correction/correction_impact_report.md`.

Le perimetre robuste realise est donc :

```text
JSON HTR -> validation schema -> EDA -> normalisation deterministe -> tokenisation -> lemmatisation -> correction lexicale -> JSON NLP -> splits + hash
```
