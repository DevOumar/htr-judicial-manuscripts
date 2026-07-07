# Rapport de conformité MD5

## Objectif

Ce rapport compare le dépôt actuel aux exigences du projet MD5 Computer Vision. Les éléments existants ont été vérifiés avant toute modification. Les éléments déjà conformes ont été documentés au lieu d'être recréés. Les éléments manquants ont été ajoutés lorsque cela était possible sans relancer de gros entraînements.

## Checklist de conformité

| Exigence | Statut | Fichier / dossier | Conforme |
|---|---|---|---|
| Prétraitement image | Présent | `src/preprocessing/preprocess.py`, `docs/PREPROCESSING_PIPELINE.md` | Oui |
| Deskew | Présent | `src/preprocessing/preprocess.py` | Oui |
| CLAHE | Présent | `src/preprocessing/preprocess.py` | Oui |
| Sauvola | Présent | `src/preprocessing/preprocess.py` | Oui |
| Configuration reproductible | Présent | `config.yaml` | Oui |
| Conventions de transcription | Présent | `CONVENTIONS_TRANSCRIPTION.md` | Oui |
| Schéma JSON | Ajouté | `schemas/transcription_schema.json` | Oui |
| Validation JSON | Ajoutée et exécutée | `src/evaluation/validate_data_contract.py`, `outputs/data_contract_validation/` | Oui |
| Score de confiance par ligne | Ajouté | `src/evaluation/quality_flags.py`, `outputs/judicial_demo/*/transcriptions.json` | Oui |
| `needs_review` par ligne | Ajouté | `src/evaluation/quality_flags.py`, `docs/QUALITY_FLAGS.md` | Oui |
| CER bootstrap IC95 | Présent | `src/evaluation/bootstrap.py`, `outputs/evaluation/bootstrap_cer_wer.json` | Oui |
| WER bootstrap IC95 | Présent | `src/evaluation/bootstrap.py`, `outputs/evaluation/bootstrap_cer_wer.json` | Oui |
| Hash SHA-256 du corpus | Ajouté | `src/evaluation/dataset_hashes.py`, `artifacts/dataset_hashes.json` | Oui |
| IoU segmentation | Implémenté | `src/evaluation/segmentation_iou.py`, `docs/SEGMENTATION_EVALUATION.md` | Partiel |
| Sources de données | Présent | `DATA_SOURCES.md` | Oui |
| Audit docstrings | Ajouté | `src/evaluation/docstring_audit.py`, `outputs/docstring_audit/docstring_audit_report.json` | Oui |
| Journal d'expériences | Présent | `experiments/journal.jsonl` | Oui |
| Sortie NLP enrichie | Ajoutée | `src/nlp/enrich_dataset.py`, `dataset_nlp/nlp/transcriptions_enriched.json` | Oui |
| Schéma NLP | Ajouté | `schemas/nlp_schema.json` | Oui |
| Validation schéma NLP | Ajoutée et exécutée | `schemas/nlp_schema.json` | Oui |

## Résultats bootstrap

Source : `outputs/evaluation/bootstrap_cer_wer.json`

Les métriques CER/WER sont calculées avec intervalle de confiance bootstrap à 95 %. Sur la vérité terrain judiciaire validée, le projet fournit également un rapport final dans :

- `outputs/judicial_gt_evaluation/final_judicial_evaluation_report.md`

Résultats principaux :

- CER brut : 13,01 %
- WER brut : 45,82 %
- CER après correction : 10,75 %
- WER après correction : 40,11 %

## IoU segmentation

L'IoU est implémenté, mais la mesure numérique n'est pas démontrable sur le corpus judiciaire Gallica, car les pages ne fournissent pas de polygones de vérité terrain. Le script indique cette limite explicitement. Ce point est donc conforme sur le plan de l'implémentation, mais partiel sur le plan expérimental.

## Docstrings

Un audit des docstrings est disponible dans :

- `outputs/docstring_audit/docstring_audit_report.json`

Les nouveaux modules de conformité contiennent des docstrings, mais certains modules historiques restent perfectibles. Ce point est acceptable pour le rendu, avec amélioration possible.

## Exigences NLP liées

| Exigence NLP | Statut | Fichier |
|---|---|---|
| Normalisation linguistique | Présent | `src/nlp/normalization.py`, `CONVENTIONS_NLP.md` |
| Correction post-HTR | Présent | `src/nlp/correction.py`, `docs/POST_HTR_CORRECTION.md` |
| Schéma BIO | Présent | `data/ner/bio_sample.csv` |
| Alignement WordPiece avec `-100` | Présent | `src/nlp/ner_training.py` |
| POS / lemmatisation | Présent en version simple et backend optionnel | `src/nlp/pos_external.py` |
| TEI XML | Présent | `dataset_nlp/advanced/transcription_tei.xml` |

Le projet ne prétend pas avoir entraîné un modèle CamemBERT complet. Il fournit un scaffold d'entraînement et un échantillon annoté minimal, ce qui correspond à l'objectif de validation du pipeline.

## Pourcentage global de conformité

Total d'exigences évaluées : 26  
Exigences conformes : 24  
Exigences partiellement conformes : 2  
Exigences non conformes : 0

Conformité globale estimée :

```text
92 %
```

## Limites honnêtes

1. L'IoU ne peut pas être calculé sur les pages Gallica sans polygones de référence.
2. Certains modules anciens pourraient recevoir davantage de docstrings.
3. La qualité HTR s'est améliorée avec Kraken, mais reste une limite de performance modèle.
4. Le fine-tuning massif CATMuS n'a pas été lancé.

## Conclusion

Le projet est largement conforme aux exigences MD5. Il est reproductible et auditable pour le prétraitement, la segmentation, l'évaluation HTR, le contrat JSON, l'enrichissement NLP, les indicateurs de qualité, les intervalles bootstrap, les hash de corpus et le suivi d'expériences.
