# Conventions de transcription

## Niveau retenu

Le projet utilise une transcription semi-diplomatique.

Objectif : conserver les formes graphiques utiles pour l'HTR et l'analyse historique, tout en normalisant uniquement ce qui facilite l'encodage informatique et l'évaluation.

## Principes

- Graphie originale conservée autant que possible.
- Abréviations conservées si elles sont visibles dans l'image.
- Pas de modernisation orthographique.
- Pas de correction grammaticale.
- Ponctuation conservée lorsqu'elle est lisible.
- Casse conservée lorsque l'information est clairement lisible ; sinon, casse minuscule acceptée pour l'entraînement.
- Espaces régularisés pour éviter les doubles espaces artificiels.

## Abréviations

Les abréviations ne sont pas développées automatiquement.

| Cas | Transcription |
|---|---|
| Forme abrégée de "ledit" | `led.` si le point abréviatif est visible |
| Suspension illisible | forme visible uniquement, sinon `[UNK]` |

## Caractères spéciaux et Unicode

- Encodage : UTF-8.
- Guillemets, accents et caractères français sont conservés s'ils sont présents dans la référence.
- Les caractères non nécessaires à l'HTR peuvent être normalisés en NFC.
- Les ligatures typographiques modernes ne sont pas introduites artificiellement.

## Lacunes et illisible

| Cas | Convention |
|---|---|
| Texte illisible court | `[UNK]` |
| Lacune matérielle | `[...]` |
| Mot partiellement lisible | conserver les caractères lisibles et signaler si nécessaire avec `[UNK]` |
| Ligne non transcrivable | `[UNK]` |

## Exemples

| Cas | Transcription |
|---|---|
| Graphie ancienne lisible | `par devant nous` |
| Abréviation conservée | `led. registre` |
| Lacune | `a comparu [...] devant la cour` |
| Illisible | `[UNK]` |

## Usage dans le projet

Ces conventions s'appliquent aux transcriptions CATMuS, aux exemples de vérité terrain locaux et aux annotations manuelles du corpus Parlement de Paris.

Les sorties automatiques conservent le champ brut `prediction` et l'alias contractuel `transcription`.
