# HTR-Judicial-Manuscripts : pipeline reproductible pour manuscrits judiciaires français

## Résumé

Ce projet développe un pipeline de Computer Vision, HTR et NLP pour des manuscrits judiciaires français anciens. À partir de pages Gallica issues des registres du Parlement de Paris, la chaîne télécharge les images via IIIF, applique un prétraitement documentaire, segmente les pages avec Kraken, extrait les lignes, transcrit avec un modèle Kraken spécialisé en manuscrits français, puis exporte les résultats en PAGE XML et JSON pour le module NLP.

Le pipeline traite 5 pages complètes, 247 lignes extraites automatiquement et 100 lignes validées manuellement pour l'évaluation. Sur cette vérité terrain judiciaire, le CER brut est de 13,01 % et le WER brut de 45,82 %. Après correction post-HTR, le CER descend à 10,75 % et le WER à 40,11 %.

## 1. Introduction

Les bibliothèques et services d'archives mettent en ligne de nombreux manuscrits anciens, mais ces documents restent difficiles à interroger automatiquement. Les registres judiciaires posent un problème particulier : ils contiennent une écriture manuscrite ancienne, des graphies variables, des abréviations et une mise en page complexe.

L'objectif du projet est de produire un pipeline reproductible capable de transformer une page manuscrite numérisée en données textuelles structurées et exploitables.

## 2. Données

Deux types de données ont été considérés.

Le corpus de développement est CATMuS. Il contient des lignes manuscrites historiques avec transcriptions et constitue une ressource pertinente pour un futur fine-tuning à grande échelle. Une analyse du projet estime qu'environ 56 000 lignes françaises peuvent être exploitées. Aucun entraînement massif sur ces lignes n'a toutefois été lancé dans la version actuelle.

Le corpus métier principal est constitué de registres judiciaires du Parlement de Paris, disponibles via Gallica/BnF.

Informations principales :

- institution : Bibliothèque nationale de France / Gallica ;
- identifiant : `btv1b9062074w` ;
- période : 1643-1644 ;
- type : registres judiciaires ;
- accès : images IIIF ;
- pages traitées : 5 ;
- lignes extraites : 247 ;
- lignes validées manuellement : 100.

## 3. Méthode

Le pipeline suit les étapes suivantes :

```text
Gallica / IIIF
-> prétraitement
-> segmentation Kraken
-> extraction des lignes
-> HTR Kraken
-> PAGE XML
-> JSON
-> correction post-HTR
-> enrichissement NLP
```

Le prétraitement comprend la correction d'inclinaison, CLAHE et la binarisation adaptative Sauvola. La segmentation est réalisée avec Kraken. Les lignes extraites sont transcrites avec Kraken OCR et le modèle `ManuMcFrenchV3.mlmodel`, plus adapté aux manuscrits français historiques que les baselines TrOCR testées.

Les sorties sont produites en PAGE XML, JSON et fichiers texte de page.

## 4. Évaluation

L'évaluation HTR repose sur 100 lignes validées manuellement issues du corpus judiciaire.

| État | CER | WER |
|---|---:|---:|
| Transcription brute | 13,01 % | 45,82 % |
| Après correction post-HTR | 10,75 % | 40,11 % |

Intervalles de confiance bootstrap à 95 % :

| État | CER IC95 | WER IC95 |
|---|---|---|
| Brut | [11,96 %, 14,19 %] | [42,22 %, 49,58 %] |
| Corrigé | [9,62 %, 12,05 %] | [36,34 %, 44,10 %] |

## 5. NLP

Le volet NLP exploite le JSON produit par le pipeline HTR. Il inclut :

- normalisation linguistique ;
- correction post-HTR ;
- tokenisation ;
- lemmatisation simple ;
- entités nommées rule-based ;
- relations simples ;
- export TEI XML.

Un scaffold CamemBERT NER est présent pour montrer le schéma BIO, l'alignement WordPiece et l'utilisation de `-100` pour les sous-tokens de continuation. Le modèle CamemBERT complet n'a pas été entraîné dans la version actuelle.

## 6. Discussion

Les résultats montrent que le pipeline est fonctionnel de bout en bout. La segmentation est exploitable et les exports PAGE XML / JSON permettent un traitement NLP structuré.

La transcription reste cependant imparfaite. Le CER est raisonnable pour une démonstration universitaire, mais le WER reste élevé. Les erreurs principales concernent les mots collés, les graphies anciennes, les abréviations et les confusions de lettres.

La correction post-HTR améliore les scores, mais ne remplace pas une validation humaine lorsqu'une transcription scientifique est attendue.

## 7. Conclusion

Le projet livre un pipeline complet, auditable et reproductible, du scan brut au JSON NLP. La meilleure solution actuelle repose sur Kraken OCR avec un modèle manuscrit français spécialisé. Les pistes d'amélioration principales sont l'extension de la vérité terrain judiciaire et un fine-tuning à grande échelle sur GPU avec CATMuS français et des lignes Parlement de Paris annotées.

## Références indicatives

- Kraken OCR.
- Microsoft TrOCR.
- CATMuS.
- HTR-United.
- PAGE XML.
- Bibliothèque nationale de France, Gallica.
