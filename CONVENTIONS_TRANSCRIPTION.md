# Conventions De Transcription

## Niveau retenu

Le projet utilise une transcription semi-diplomatique.

Objectif: conserver les formes graphiques utiles pour l'HTR et l'analyse historique, tout en normalisant uniquement ce qui facilite l'encodage informatique et l'evaluation.

## Principes

- Graphie originale conservee autant que possible.
- Abreviations conservees si elles sont visibles dans l'image.
- Pas de modernisation orthographique.
- Pas de correction grammaticale.
- Ponctuation conservee lorsqu'elle est lisible.
- Casse conservee lorsque l'information est clairement lisible; sinon casse minuscule acceptee pour l'entrainement.
- Espaces regularises pour eviter les doubles espaces artificiels.

## Abreviations

Les abreviations ne sont pas developpees automatiquement.

| Cas | Transcription |
| --- | --- |
| Forme abregee de "ledit" | `led.` si le point abreviatif est visible |
| Suspension illisible | forme visible uniquement, sinon `[UNK]` |

## Caracteres Speciaux Et Unicode

- Encodage: UTF-8.
- Guillemets, accents et caracteres francais sont conserves s'ils sont presents dans la reference.
- Les caracteres non necessaires a l'HTR peuvent etre normalises en NFC.
- Les ligatures typographiques modernes ne sont pas introduites artificiellement.

## Lacunes Et Illisible

| Cas | Convention |
| --- | --- |
| Texte illisible court | `[UNK]` |
| Lacune materielle | `[...]` |
| Mot partiellement lisible | conserver les caracteres lisibles et signaler si necessaire avec `[UNK]` |
| Ligne non transcrivable | `[UNK]` |

## Exemples

| Cas | Transcription |
| --- | --- |
| Graphie ancienne lisible | `par devant nous` |
| Abreviation conservee | `led. registre` |
| Lacune | `a comparu [...] devant la cour` |
| Illisible | `[UNK]` |

## Usage Dans Le Projet

Ces conventions s'appliquent aux transcriptions CATMuS, aux exemples de ground truth locaux et aux futures annotations manuelles du corpus Parlement de Paris.

Les sorties automatiques conservent le champ brut `prediction` et l'alias contractuel `transcription`.
