# Audit du code

## Périmètre

Cet audit couvre la structure du dépôt, les modules source, les artefacts générés, les dépendances et les sorties de validation utilisées par le pipeline HTR actuel :

```text
Gallica / IIIF
-> prétraitement
-> Kraken
-> segmentation
-> extraction des lignes
-> HTR
-> PAGE XML
-> JSON
-> transcription complète
```

## État des composants

| Composant | Statut | Fichiers principaux |
|---|---|---|
| Chargement CATMuS | Fonctionnel | `src/dataset/load_dataset.py`, `src/dataset/visualize.py` |
| Entraînement / évaluation TrOCR | Fonctionnel comme baseline | `src/htr/train_trocr.py`, `src/htr/data.py`, `src/htr/metrics.py`, `src/evaluation/evaluate.py` |
| Prétraitement image | Fonctionnel | `src/preprocessing/preprocess.py` |
| Segmentation Kraken | Fonctionnel | `src/segmentation/kraken_segmentation.py` |
| Transcription de crops de lignes | Fonctionnel | `src/segmentation/kraken_segmentation.py`, `src/evaluation/predict_line_crops.py`, `src/evaluation/predict_kraken_crops.py` |
| Export PAGE XML | Fonctionnel dans le pipeline | `src/segmentation/kraken_segmentation.py` |
| Export JSON et transcription page | Fonctionnel dans le pipeline | `src/segmentation/kraken_segmentation.py` |
| Validation PAGE XML | Ajoutée | `src/evaluation/page_xml_validation.py` |
| Validation de l'ordre de lecture | Ajoutée | `src/evaluation/reading_order_validation.py` |
| Analyse qualité des crops | Ajoutée | `src/evaluation/crop_quality_analysis.py` |
| Analyse des échecs HTR | Ajoutée | `src/evaluation/htr_failure_analysis.py` |
| Benchmark modèles | Ajouté | `src/evaluation/model_benchmark.py` |
| Test d'artefacts pipeline complet | Ajouté | `src/tests/test_full_pipeline.py` |

## Nettoyage effectué

Les anciens scripts prototypes et fichiers obsolètes ont été identifiés puis retirés lorsqu'ils n'étaient plus nécessaires au pipeline reproductible.

Exemples de fichiers considérés comme obsolètes :

- scripts d'export prototype avec données codées en dur ;
- sorties générées anciennes non utilisées ;
- fichiers temporaires de présentation ;
- caches locaux non destinés au dépôt GitHub.

Les dossiers suivants restent volontairement présents localement ou documentés :

- `outputs/` : sorties de validation et démonstration ;
- `models/` : modèles locaux non poussés sur GitHub ;
- `data/cache/` : cache utile pour travailler hors ligne avec CATMuS ;
- `experiments/journal.jsonl` : journal minimal des expériences.

## Dépendances

`requirements.txt` est cohérent avec les composants implémentés :

- HTR et modèles : `torch`, `transformers`, `datasets`, `evaluate`, `jiwer` ;
- vision et documents : `opencv-python`, `scikit-image`, `matplotlib`, `jdeskew` ;
- XML / JSON / validation : bibliothèques standard et `jsonschema` ;
- NLP : outils simples de normalisation, tokenisation et enrichissement.

Certaines dépendances restent optionnelles pour des perspectives de fine-tuning ou d'expérimentation, par exemple `peft`.

## Artefacts de validation

| Dossier | Contenu |
|---|---|
| `outputs/page_xml_validation/` | Validation structurelle PAGE XML |
| `outputs/reading_order/` | Rapports et visualisations d'ordre de lecture |
| `outputs/crop_analysis/` | Statistiques et visualisations sur les crops |
| `outputs/htr_analysis/` | Analyse des échecs HTR |
| `outputs/model_benchmark/` | Comparaison de modèles HTR |

## Limites restantes

1. La qualité HTR reste le point le plus fragile scientifiquement.
2. Les pages Gallica judiciaires ne fournissent pas de vérité terrain géométrique, donc l'IoU ne peut pas être calculé directement sur ce corpus.
3. L'ordre de lecture est dérivé de Kraken. Il est compatible avec une lecture par colonnes, mais doit être validé visuellement sur les cas ambigus.
4. Les modèles TrOCR Base/Large sont coûteux sur CPU.
5. La validation PAGE XML vérifie la structure produite par le projet, mais pas une validation XSD externe complète.

## Conclusion

Le dépôt a été nettoyé sans supprimer les artefacts nécessaires à la reproductibilité. Le pipeline est complet, auditable et organisé. Les limites restantes concernent surtout la qualité HTR et la disponibilité de vérités terrain spécialisées, pas la structure du code.
