# Dataset de transcriptions NLP

Ce dossier contient le jeu de données JSON demandé pour le volet NLP du projet MD5.

- `transcriptions.json` : dataset plat au niveau ligne, validé par `schemas/transcription_schema.json`.
- `page_*.json` : datasets organisés par page.
- `metadata.json` : métadonnées du corpus, des sources et des fichiers.
- `nlp/` : sorties enrichies avec normalisation, tokens, lemmes et statistiques.
- `advanced/` : sorties exploratoires NER, relations, graphe et TEI.
- `splits/` : partitions train / validation / test.

Source HTR utilisée : `kraken`.

Important : le texte actuel est généré automatiquement par HTR. Il doit être relu pour un usage scientifique ou éditorial. Les champs `needs_review` et `confidence` servent à prioriser la correction manuelle. Les prédictions brutes vides sont exportées sous la forme `[UNK]` afin de conserver des fichiers PAGE XML et JSON structurellement valides.
