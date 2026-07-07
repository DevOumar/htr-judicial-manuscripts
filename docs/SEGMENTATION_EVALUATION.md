# Évaluation géométrique de la segmentation

L'évaluation IoU géométrique est implémentée dans :

- `src/evaluation/segmentation_iou.py`

## Mesure

Les polygones prédits et les polygones de référence sont rasterisés sous forme de masques binaires. L'IoU est ensuite calculé ainsi :

```text
IoU = aire(intersection) / aire(union)
```

Cette mesure permet d'évaluer la qualité géométrique d'une segmentation lorsque des polygones de référence sont disponibles.

## Limite sur le corpus judiciaire

Les pages Gallica du corpus judiciaire ne fournissent pas de polygones de vérité terrain ligne par ligne. L'IoU ne peut donc pas être calculé directement sur le corpus final Parlement de Paris.

Le script calcule l'IoU uniquement si une sortie contient :

- des polygones prédits ;
- des polygones de référence comparables ;
- une correspondance entre lignes prédites et lignes de référence.

Cette implémentation reste utile pour valider la segmentation sur CATMuS lorsque les polygones de référence sont disponibles.

## Commande

```bash
python src/evaluation/segmentation_iou.py --input-dir outputs/segmentation
```

Si aucun polygone de référence comparable n'est disponible, le rapport indique explicitement `missing_reference` ou `no_comparable_polygons`. Il s'agit d'une limite des données, pas d'un échec du pipeline.
