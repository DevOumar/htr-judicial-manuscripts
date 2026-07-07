# Sélection du corpus judiciaire

Le corpus technique de développement reste `CATMuS/medieval` et `CATMuS/medieval-segmentation`.

Le corpus métier final est constitué de documents judiciaires ou administratifs français anciens, avec priorité aux pages complètes exploitables par Kraken.

## Sources comparées

| Source | URL | Institution | Période | Qualité des images | Transcriptions | Pertinence juridique | Décision |
|---|---|---|---|---|---|---|---|
| Copie de registres du Parlement de Paris, Français 21256 | https://gallica.bnf.fr/ark:/12148/btv1b9062074w | BnF / Gallica | 1643-1644 | Images IIIF pleine page, adaptées à Kraken | Non disponibles en format directement exploitable | Très forte : registres du Parlement de Paris | Sélectionnée pour la démonstration finale |
| Collection de copies et extraits des registres du Parlement de Paris, principaux procès criminels | https://gallica.bnf.fr/ark:/12148/btv1b525273066 | BnF / Gallica | XVIIe-XVIIIe siècles | Images Gallica pleine page | Non disponibles en format exploitable | Forte : procédures criminelles et extraits parlementaires | Source pertinente mais plus hétérogène |
| Inventaire du greffe de la maison consulaire de Montpellier | Archives municipales de Montpellier, manuscrits II 10 / II 11 | Archives municipales de Montpellier | 1662-1663 | Accès image complet non confirmé | Édition partielle imprimée postérieure | Moyenne à forte : greffe et archive administrative | Non retenu pour le téléchargement reproductible |

## Corpus retenu

Le corpus retenu est le registre Gallica/BnF :

- identifiant : `btv1b9062074w`
- institution : Bibliothèque nationale de France / Gallica
- type : registres judiciaires du Parlement de Paris
- période : 1643-1644
- accès : images IIIF
- licence et usage : consultation académique via Gallica/BnF

## Démonstration

La démonstration actuelle télécharge 5 images de page et exécute :

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

Les résultats sont générés dans :

- `outputs/judicial_demo/`

Ce choix est le plus robuste pour le projet : il correspond au domaine juridique, les images sont accessibles de manière reproductible, et le format pleine page permet de valider le pipeline complet.
