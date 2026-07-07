# Plan de sauvetage HTR

## Question centrale

Comment obtenir une transcription réellement lisible sur les registres judiciaires du Parlement de Paris ?

## Réponse courte

Le meilleur choix immédiat est d'utiliser Kraken OCR avec le modèle `ManuMcFrenchV3.mlmodel`, spécialisé dans les manuscrits français. TrOCR reste utile comme baseline et comme piste de fine-tuning, mais les modèles TrOCR testés directement ne sont pas assez adaptés aux écritures judiciaires françaises du XVIIe siècle.

## État actuel

Le pipeline fonctionne :

```text
Gallica
-> IIIF
-> prétraitement
-> Kraken segmentation
-> lignes
-> HTR
-> PAGE XML
-> JSON
-> NLP
```

Le problème n'est donc plus le pipeline. Le problème est la qualité du moteur HTR.

## Modèle actuellement recommandé

- moteur : Kraken OCR ;
- modèle : `ManuMcFrenchV3.mlmodel` ;
- type : modèle de reconnaissance pour manuscrits français ;
- référence : `10.5281/zenodo.10874058` ;
- confiance moyenne estimée : 0,9477 ;
- temps moyen : environ 0,0757 seconde par ligne.

Ce modèle est le meilleur moteur pratique actuellement intégré dans le dépôt.

## Résultats mesurés

Évaluation sur 100 lignes du Parlement de Paris validées manuellement :

| Système | CER | WER |
|---|---:|---:|
| Kraken brut | 13,01 % | 45,82 % |
| Kraken + correction post-HTR | 10,75 % | 40,11 % |

Le CER devient exploitable pour une démonstration universitaire. Le WER reste élevé, ce qui confirme que les mots collés, les graphies anciennes et les erreurs lexicales restent difficiles.

## Comparaison des solutions

### TrOCR Small

Avantages :

- simple à utiliser avec Hugging Face ;
- rapide ;
- bonne baseline.

Inconvénients :

- surtout adapté à l'écriture manuscrite moderne anglophone ;
- faible adaptation aux manuscrits français anciens ;
- sorties parfois peu lisibles.

Compatibilité :

- excellente avec le pipeline TrOCR existant.

Décision :

- à conserver comme baseline, pas comme moteur final.

### TrOCR Base

Avantages :

- capacité plus élevée que Small ;
- compatible avec le code existant.

Inconvénients :

- plus lent sur CPU ;
- pas spécialisé ancien français ;
- la taille du modèle ne corrige pas seule le décalage de domaine.

Décision :

- intéressant seulement avec fine-tuning sérieux sur GPU.

### TrOCR Large

Avantages :

- capacité importante.

Inconvénients :

- trop coûteux pour CPU ;
- bénéfice incertain sans données adaptées ;
- pas prioritaire pour un projet court.

Décision :

- non prioritaire.

### `dj0w/trocr-french-handwriting-v5`

Avantages :

- modèle français ;
- compatible Hugging Face / TrOCR ;
- bon point de départ potentiel.

Inconvénients :

- entraîné sur écriture française moderne ;
- transfert faible vers les manuscrits judiciaires du XVIIe siècle.

Décision :

- bon point de départ pour fine-tuning, pas assez bon comme solution directe.

### PyLaia CATMuS

Avantages :

- entraîné sur manuscrits historiques ;
- plus proche du domaine que TrOCR moderne ;
- candidat très sérieux.

Inconvénients :

- pas compatible directement avec `TrOCRProcessor` ;
- nécessite un backend PyLaia séparé ;
- intégration plus longue.

Décision :

- à tester en priorité si le temps permet d'ajouter un backend PyLaia propre.

### Kraken OCR

Avantages :

- déjà utilisé pour la segmentation ;
- adapté aux documents historiques ;
- modèle français manuscrit disponible ;
- intégration directe sur les crops de lignes.

Inconvénients :

- nécessite la gestion d'un modèle Kraken local ;
- format différent de Hugging Face ;
- transcription encore imparfaite.

Décision :

- meilleur choix final actuel.

### HTR-United et modèles spécialisés

Avantages :

- possibilité de trouver des modèles ou corpus proches des écritures administratives ;
- utile pour la recherche de données d'entraînement.

Inconvénients :

- pas un modèle unique prêt à l'emploi ;
- formats hétérogènes ;
- intégration variable.

Décision :

- utile pour une phase future de recherche de modèles et de données.

## Rôle de CATMuS

CATMuS est le meilleur corpus de développement identifié pour un entraînement français historique à grande échelle.

Estimation utilisée dans le projet :

- environ 56 000 lignes françaises exploitables ;
- données alignées image / transcription ;
- adapté au HTR historique.

Mais il ne faut pas dire que le modèle final a été entraîné sur ces 56 000 lignes. Dans la version actuelle, CATMuS est une ressource étudiée et une perspective de fine-tuning.

## Vérité terrain judiciaire

La priorité scientifique était de créer une vérité terrain métier :

- 5 pages Parlement de Paris ;
- 247 lignes extraites ;
- 100 lignes validées manuellement ;
- calcul réel du CER/WER sur le corpus final.

Cette étape est essentielle, car sans référence judiciaire, les comparaisons de modèles restent qualitatives.

## Priorités

1. Garder Kraken `ManuMcFrenchV3.mlmodel` comme moteur final actuel.
2. Utiliser les 100 lignes judiciaires pour évaluer objectivement les sorties.
3. Étendre la vérité terrain judiciaire si plus de temps est disponible.
4. Tester PyLaia CATMuS sur les mêmes lignes.
5. Lancer un fine-tuning CATMuS français uniquement avec GPU.
6. Ajouter des lignes Parlement de Paris au fine-tuning pour une vraie adaptation de domaine.

## Conclusion

Le sauvetage le plus crédible à court terme est Kraken OCR avec modèle français spécialisé + correction post-HTR + évaluation sur vérité terrain judiciaire. La solution la plus forte à moyen terme serait un fine-tuning avec CATMuS français et des lignes Parlement de Paris validées manuellement.
