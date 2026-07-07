# Contrat de données JSON

Le contrat JSON final au niveau ligne est documenté et validé par :

- Schéma : `schemas/transcription_schema.json`
- Validateur : `src/evaluation/validate_data_contract.py`

Le contrat enrichi pour le NLP est documenté et validé par :

- Schéma : `schemas/nlp_schema.json`
- Sortie : `dataset_nlp/nlp/transcriptions_enriched.json`

## Champs principaux

| Champ | Type | Description |
|---|---|---|
| `image_id` | string | Identifiant de l'image source |
| `page_id` | string | Identifiant de la page |
| `line_id` | string | Identifiant unique de la ligne |
| `transcription` | string | Transcription retenue pour la ligne |
| `confidence` | number | Estimation de confiance entre `0` et `1` |
| `needs_review` | boolean | Indique si la ligne doit être vérifiée manuellement |
| `polygon` | array | Polygone de la ligne dans l'image page |
| `source_image` | string | Chemin de l'image source ou du crop |
| `model_name` | string | Modèle HTR utilisé |

Le champ historique `prediction` est conservé pour compatibilité et reflète le contenu de `transcription`.

## Champs NLP enrichis

| Champ | Type | Description |
|---|---|---|
| `normalized_transcription` | string | Texte normalisé par règles |
| `normalization_rules_applied` | array | Noms des règles ayant modifié la ligne |
| `tokens` | array | Tokens avec offsets |
| `lemmas` | array | Lemmes associés aux mots et nombres |
| `entities` | array | Entités détectées lorsque le pipeline avancé est exécuté |

## Validation

```bash
python src/evaluation/quality_flags.py --input-dir outputs/judicial_demo
python src/evaluation/validate_data_contract.py --input-dir outputs/judicial_demo --schema schemas/transcription_schema.json
python src/evaluation/validate_data_contract.py --input-dir dataset_nlp/nlp/transcriptions_enriched.json --schema schemas/nlp_schema.json
```

## Note sur la confiance

`confidence` est actuellement une estimation de confiance, pas une probabilité calibrée. Le pipeline utilise les probabilités du modèle lorsqu'elles sont disponibles. Pour les sorties plus anciennes, il applique une heuristique prudente fondée sur la longueur du texte, les répétitions, la taille du crop et le contraste.
