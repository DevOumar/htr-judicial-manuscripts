# Correction post-HTR

## Objectif

Cette etape repond aux consignes NLP sur :

- les regles de correction d'erreurs HTR frequentes ;
- la restauration prudente des espaces dans les mots colles ;
- le lexique de reference ;
- les suggestions automatiques ;
- la comparaison vocabulaire brut / vocabulaire corrige ;
- le calcul CER/WER avant et apres correction quand une verite terrain existe.

La correction ne remplace pas la transcription humaine. Elle produit une version
post-traitee et conserve toujours la transcription HTR originale.

## Commande

```bash
python src/nlp/correction.py --input dataset_nlp/transcriptions.json --lexicon data/lexicons/judicial_lexicon.txt --gt data/judicial_gt/judicial_gt_annotation_with_draft.csv --output-dir outputs/nlp_correction
```

## Fichiers principaux

- `data/lexicons/judicial_lexicon.txt` : lexique juridique de reference.
- `outputs/nlp_correction/corrected_transcriptions.json` : transcriptions avec correction post-HTR.
- `outputs/nlp_correction/correction_suggestions.csv` : suggestions automatiques.
- `outputs/nlp_correction/vocabulary_comparison.md` : comparaison vocabulaire brut / corrige.
- `outputs/nlp_correction/correction_impact_report.md` : impact des corrections.

## Methode

Trois niveaux sont distingues :

1. Corrections automatiques appliquees.

   Elles sont limitees a des erreurs HTR frequentes et explicites, par exemple :

   | Erreur HTR | Correction |
   | --- | --- |
   | `conseit` | `conseil` |
   | `habiians` | `habitants` |
   | `fanorablement` | `favorablement` |
   | `restablur` | `retablir` |
   | `droins` | `droits` |

2. Restauration des espaces dans les mots colles.

   Cette etape cible le probleme signale pendant l'encadrement : certains termes
   juridico-administratifs sont reconnus comme un seul bloc alors qu'ils
   correspondent a plusieurs mots. Exemple :

   | Sortie HTR | Correction |
   | --- | --- |
   | `justicemoyenne` | `justice moyenne` |
   | `bassesustce` | `basse justice` |
   | `lettrespatentes` | `lettres patentes` |
   | `procureurgeneral` | `procureur general` |
   | `foyethommage` | `foy et hommage` |

   Deux mecanismes sont utilises :

   - regles fixes pour les expressions juridiques tres sures ;
   - segmentation automatique uniquement quand un token inconnu se decompose
     clairement en deux ou trois mots du lexique de reference.

   Cette correction est volontairement prudente : elle ne cherche pas a
   reecrire toute la ligne, seulement a restaurer des espaces quand le risque de
   surcorrection est faible.

3. Suggestions lexicales non appliquees automatiquement.

   Elles utilisent la distance de Levenshtein entre le token OCR et le lexique.
   Elles sont proposees dans le CSV pour aider la correction humaine, mais ne
   modifient pas automatiquement le texte.

Cette separation evite de surcorriger des graphies anciennes ou des noms propres.

## Resultats actuels

Derniere execution :

- lignes traitees : 247 ;
- suggestions proposees : 466 ;
- corrections appliquees automatiquement : 75 ;
- lignes modifiees : 53 ;
- formes uniques brutes : 912 ;
- formes uniques corrigees : 907 ;
- lignes avec reference manuelle : 100.

La derniere execution corrige notamment :

- `justicemoyenne` -> `justice moyenne` ;
- `bassesustce` -> `basse justice` ;
- `presentmois` -> `present mois` ;
- `desparis` -> `des paris`.

## CER/WER avant et apres

Le script calcule automatiquement :

- CER avant correction ;
- WER avant correction ;
- CER apres correction ;
- WER apres correction ;
- difference avant/apres.

Mais ces scores ne sont calculables que pour les lignes ou la colonne
`reference` est remplie dans :

```text
data/judicial_gt/judicial_gt_annotation_with_draft.csv
```

Sur les 100 lignes judiciaires annotees, la derniere evaluation donne :

- CER avant : 0.1257 ;
- CER apres : 0.1075 ;
- WER avant : 0.4515 ;
- WER apres : 0.4011.
