# Évaluation bootstrap CER/WER

Les intervalles de confiance bootstrap sont implémentés dans :

- `src/evaluation/bootstrap.py`

Le script calcule :

- le CER moyen ;
- le WER moyen ;
- l'intervalle de confiance bootstrap à 95 % ;
- le nombre d'itérations bootstrap, par défaut `N = 1000`.

## Commande

```bash
python src/evaluation/bootstrap.py --predictions outputs/evaluation/french_decoder_predictions.csv --output outputs/evaluation/bootstrap_cer_wer.json --n 1000
```

## Méthode

La méthode ré-échantillonne avec remise les paires alignées `(référence, prédiction)`. Pour chaque échantillon bootstrap, le CER et le WER sont recalculés. Les percentiles 2,5 % et 97,5 % forment l'intervalle empirique à 95 %.

## Limite

Lorsque le fichier d'évaluation contient peu de lignes, les intervalles sont naturellement plus larges. Les résultats doivent donc être interprétés comme une estimation expérimentale, pas comme une performance définitive du modèle sur tous les manuscrits judiciaires.
