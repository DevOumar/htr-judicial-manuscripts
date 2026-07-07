# État technique final

## Pipeline validé

Le pipeline judiciaire complet est opérationnel :

```text
Gallica / IIIF
-> téléchargement
-> prétraitement
-> Kraken
-> segmentation
-> extraction des lignes
-> HTR
-> PAGE XML
-> JSON
-> transcription complète
-> NLP
```

## Corpus traité

- Corpus final : registres judiciaires du Parlement de Paris, Gallica/BnF.
- Identifiant : `btv1b9062074w`.
- Période : 1643-1644.
- Pages traitées : 5.
- Lignes extraites : 247.
- Lignes transcrites dans l'export final : 247.
- Lignes validées manuellement pour l'évaluation : 100.

Les sorties principales sont dans :

- `outputs/judicial_demo/`
- `data/judicial_gt/judicial_gt_annotation_with_draft.csv`
- `dataset_nlp/`

## HTR

Le moteur HTR final retenu pour la démonstration judiciaire est :

- Kraken OCR ;
- modèle `ManuMcFrenchV3.mlmodel` ;
- référence modèle : `10.5281/zenodo.10874058`.

TrOCR est conservé comme baseline et comme piste de fine-tuning, mais les sorties judiciaires finales utilisent Kraken, car les résultats sont plus lisibles sur l'écriture française historique.

## Résultats HTR

Évaluation sur les 100 lignes judiciaires validées :

| État | CER | WER |
|---|---:|---:|
| Transcription brute | 13,01 % | 45,82 % |
| Après correction post-HTR | 10,75 % | 40,11 % |

Intervalles de confiance bootstrap à 95 % :

| État | CER IC95 | WER IC95 |
|---|---|---|
| Brut | [11,96 %, 14,19 %] | [42,22 %, 49,58 %] |
| Corrigé | [9,62 %, 12,05 %] | [36,34 %, 44,10 %] |

Temps moyen de transcription :

- environ `0,0757 s` par ligne.

Confiance moyenne estimée :

- environ `0,9477`.

Cette confiance est une estimation de tri, pas une accuracy calibrée.

## PAGE XML

Les fichiers PAGE XML générés contiennent :

- les régions ;
- les lignes ;
- les coordonnées ;
- les baselines ;
- les transcriptions dans `TextLine/TextEquiv/Unicode`.

Validation sur les 5 pages :

- lignes Unicode présentes : 247 / 247 ;
- structure PAGE XML cohérente avec le namespace utilisé par le projet ;
- validation XSD externe complète non incluse localement.

## Ordre de lecture

Le pipeline reconstruit les pages selon l'ordre de lecture fourni ou déduit par Kraken. Les pages étudiées comportent des effets de colonnes. Les visualisations dans `outputs/reading_order/` permettent de vérifier les transitions.

Interprétation :

- l'ordre est compatible avec une lecture par colonnes ;
- certains sauts verticaux correspondent au passage d'une colonne à l'autre ;
- une validation visuelle reste nécessaire pour les cas ambigus.

## Qualité des crops

L'analyse des crops est disponible dans :

- `outputs/crop_analysis/`

Elle mesure notamment :

- largeur moyenne ;
- hauteur moyenne ;
- contraste ;
- lignes très petites ;
- lignes potentiellement vides ;
- lignes tronquées ;
- répétitions suspectes.

Ces informations aident à diagnostiquer les erreurs HTR.

## NLP

Le pipeline NLP est présent et séparé dans :

- `src/nlp/`

Il produit :

- normalisation linguistique ;
- correction post-HTR ;
- tokens ;
- lemmes ;
- entités rule-based ;
- relations simples ;
- export TEI XML ;
- graphe de relations.

Les fichiers importants sont :

- `CONVENTIONS_NLP.md`
- `docs/NLP_PIPELINE.md`
- `docs/POST_HTR_CORRECTION.md`
- `docs/ADVANCED_NLP_PRESENTATION.md`
- `dataset_nlp/advanced/transcription_tei.xml`

Le projet contient aussi :

- `src/nlp/ner_training.py` : scaffold CamemBERT NER ;
- `data/ner/bio_sample.csv` : 224 tokens annotés BIO ;
- alignement WordPiece avec `-100` documenté dans le code.

Important : le projet ne prétend pas avoir entraîné un modèle CamemBERT final. Le NER avancé est un scaffold et une démonstration rule-based.

## Correction post-HTR

La correction post-HTR traite notamment :

- confusions fréquentes de caractères ;
- mots collés ;
- formes judiciaires fréquentes ;
- normalisation prudente.

Exemple :

```text
touse justicemoyenne
-> toute justice moyenne
```

La correction améliore les scores mesurés, mais ne remplace pas une transcription paléographique humaine.

## Tests

Les vérifications principales sont :

```bash
python -m compileall src
python -m pytest
```

Dernier état connu :

- 17 tests passants.

Les tests couvrent notamment :

- contrat JSON ;
- normalisation ;
- correction post-HTR ;
- tokenisation / lemmatisation ;
- structure des artefacts du pipeline.

## Ce qui fonctionne

- Téléchargement IIIF Gallica.
- Prétraitement image.
- Segmentation Kraken.
- Extraction de lignes.
- Transcription HTR de toutes les lignes.
- PAGE XML enrichi avec transcriptions.
- JSON final exploitable.
- Vérité terrain judiciaire de 100 lignes.
- Calcul CER/WER.
- Intervalles bootstrap.
- Correction post-HTR.
- Enrichissement NLP.
- Export TEI XML.
- Tests automatisés.

## Ce qui reste limité

- La transcription reste imparfaite pour un usage paléographique strict.
- Le WER reste élevé, car les mots collés, graphies anciennes et abréviations sont difficiles.
- L'IoU ne peut pas être calculé sur les pages Gallica sans polygones de référence.
- Le fine-tuning massif sur CATMuS n'a pas été lancé.
- Le NER CamemBERT complet est préparé mais non entraîné.

## Recommandations

1. Conserver Kraken `ManuMcFrenchV3.mlmodel` comme moteur HTR final actuel.
2. Conserver TrOCR comme baseline et piste future.
3. Utiliser les 100 lignes judiciaires validées comme base d'évaluation scientifique.
4. Étendre progressivement la vérité terrain à plus de lignes si l'objectif devient la qualité HTR.
5. Lancer un fine-tuning sur CATMuS ou sur des lignes judiciaires annotées uniquement si un GPU est disponible.

## Conclusion

Le projet est techniquement cohérent, reproductible et soutenable pour une démonstration universitaire complète CV + HTR + NLP. Le pipeline est validé de bout en bout. La principale limite restante est la qualité intrinsèque de la transcription automatique sur des manuscrits judiciaires anciens, malgré l'amélioration obtenue par le modèle Kraken spécialisé et les corrections post-HTR.
