# Pipeline NLP

## Objectif

L'étape NLP commence après le HTR. Elle ne remplace pas la correction manuelle et ne prétend pas produire une transcription philologique parfaite. Son rôle est de rendre les transcriptions automatiques exploitables pour une analyse NLP :

- texte normalisé ;
- tokens ;
- lemmes conservateurs ;
- statistiques lexicales ;
- corrections post-HTR prudentes ;
- JSON de sortie pour le volet NLP.

## Commandes

```bash
python src/nlp/eda.py --input dataset_nlp/transcriptions.json --output-dir outputs/nlp_eda
python src/nlp/create_splits.py --input dataset_nlp/transcriptions.json --output-dir dataset_nlp/splits --hash-output artifacts/nlp_dataset_hashes.json --seed 42
python src/nlp/enrich_dataset.py --input dataset_nlp/transcriptions.json --output-dir dataset_nlp/nlp
python src/nlp/correction.py --input dataset_nlp/transcriptions.json --lexicon data/lexicons/judicial_lexicon.txt --gt data/judicial_gt/judicial_gt_annotation_with_draft.csv --output-dir outputs/nlp_correction
python src/evaluation/validate_data_contract.py --input-dir dataset_nlp/nlp/transcriptions_enriched.json --schema schemas/nlp_schema.json
```

## Sorties

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
- `outputs/nlp_correction/corrected_transcriptions.json`
- `outputs/nlp_correction/correction_suggestions.csv`
- `outputs/nlp_correction/vocabulary_comparison.md`
- `outputs/nlp_correction/correction_impact_report.md`

## Méthode

Le pipeline NLP actuel est volontairement simple et reproductible :

1. Validation du schéma JSON.
2. EDA sur la confiance, la longueur des lignes, `needs_review` et les abréviations résiduelles.
3. Création déterministe des splits avec hash SHA-256.
4. Normalisation Unicode NFC.
5. Harmonisation des apostrophes.
6. Développement de certaines abréviations avec tilde.
7. Tokenisation par expressions régulières en conservant mots, nombres et ponctuation.
8. Lemmatisation conservatrice du français historique.
9. Correction post-HTR prudente avec lexique et distance de Levenshtein.
10. Rapport d'impact avant/après correction.

## Où voir la normalisation

Ouvrir :

```text
dataset_nlp/nlp/transcriptions_enriched.json
```

Champs importants :

- `transcription` : sortie HTR brute utilisée par le projet ;
- `normalized_transcription` : texte harmonisé en Unicode NFC ;
- `rule_normalized_transcription` : texte après règles NLP ;
- `normalization_rules_applied` : règles effectivement appliquées ;
- `tokens` : tokens avec offsets ;
- `lemmas` : lemmes extraits.

## Où voir la correction post-HTR

Ouvrir :

```text
outputs/nlp_correction/correction_suggestions.csv
outputs/nlp_correction/vocabulary_comparison.md
outputs/nlp_correction/correction_impact_report.md
```

La correction automatique est volontairement prudente. Les suggestions lexicales sont proposées, mais elles ne sont pas toutes appliquées automatiquement afin d'éviter de corriger à tort des graphies anciennes.

## Limites

- Les lemmes sont approximatifs.
- Les erreurs OCR se propagent dans la tokenisation et la lemmatisation.
- La correction guidée par confiance au niveau caractère n'est pas appliquée, car l'export Kraken actuel fournit une confiance ligne, mais pas `char_confidences` ni `candidates`.
- Le vrai CER/WER judiciaire avant/après correction est calculé sur les 100 lignes de vérité terrain validées dans `data/judicial_gt/judicial_gt_annotation_with_draft.csv`.
