# Pipeline de prétraitement d'image

Le pipeline de prétraitement existe dans :

- `src/preprocessing/preprocess.py`

Il couvre les exigences image du projet MD5 :

| Exigence | Statut | Implémentation |
|---|---|---|
| Correction d'inclinaison / deskew | Présent | `preprocess_image()` avec `jdeskew.get_angle()` et `rotate()` |
| CLAHE | Présent | amélioration locale du contraste |
| Binarisation adaptative Sauvola | Présent | seuillage local adapté aux manuscrits |
| Paramétrisation reproductible | Présent | paramètres dans `config.yaml` et arguments CLI |

## Étapes

1. Lecture de l'image en niveaux de gris.
2. Estimation de l'angle d'inclinaison avec `jdeskew`.
3. Rotation de l'image pour corriger l'inclinaison.
4. Application de CLAHE pour améliorer le contraste local.
5. Application de la binarisation adaptative de Sauvola.
6. Sauvegarde de l'image prétraitée.

## Justification scientifique

La correction d'inclinaison améliore la segmentation en alignant les lignes d'écriture. CLAHE est adapté aux manuscrits historiques, car l'éclairage, l'encre et l'état du papier varient localement. La binarisation de Sauvola est une méthode standard pour les images de documents où un seuil global échoue à cause du vieillissement du papier, des taches, des ombres ou d'une densité d'encre hétérogène.

## Commande

```bash
python src/preprocessing/preprocess.py --config config.yaml --input-dir data/raw --output-dir data/processed
```

## Exemples avant / après

Lorsque les données locales sont présentes, les images avant/après sont stockées dans :

- `data/raw/`
- `data/processed/`

Pour la démonstration judiciaire, le prétraitement reste volontairement conservateur : le pipeline de segmentation redimensionne les pages complètes pour Kraken, tandis que ce module autonome documente et valide la chaîne de traitement d'image demandée dans le brief MD5.
