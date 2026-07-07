# Correction post-HTR

## Objectif

Cette étape répond aux consignes NLP sur :

- les règles de correction d'erreurs HTR fréquentes ;
- la restauration prudente des espaces dans les mots collés ;
- le lexique de référence ;
- les suggestions automatiques ;
- la comparaison vocabulaire brut / vocabulaire corrigé ;
- le calcul CER/WER avant et après correction quand une vérité terrain existe.

La correction ne remplace pas la transcription humaine. Elle produit une version post-traitée et conserve toujours la transcription HTR originale.

## Commande

```bash
python src/nlp/correction.py --input dataset_nlp/transcriptions.json --lexicon data/lexicons/judicial_lexicon.txt --gt data/judicial_gt/judicial_gt_annotation_with_draft.csv --output-dir outputs/nlp_correction
```

## Fichiers principaux

- `data/lexicons/judicial_lexicon.txt` : lexique juridique de référence.
- `outputs/nlp_correction/corrected_transcriptions.json` : transcriptions avec correction post-HTR.
- `outputs/nlp_correction/correction_suggestions.csv` : suggestions automatiques.
- `outputs/nlp_correction/vocabulary_comparison.md` : comparaison vocabulaire brut / corrigé.
- `outputs/nlp_correction/correction_impact_report.md` : impact des corrections.

## Méthode

Trois niveaux sont distingués :

1. Corrections automatiques appliquées.

   Elles sont limitées à des erreurs HTR fréquentes et explicites, par exemple :

   | Erreur HTR | Correction |
   |---|---|
   | `conseit` | `conseil` |
   | `habiians` | `habitants` |
   | `fanorablement` | `favorablement` |
   | `restablur` | `rétablir` |
   | `droins` | `droits` |

2. Restauration des espaces dans les mots collés.

   Cette étape cible le problème signalé pendant l'encadrement : certains termes juridico-administratifs sont reconnus comme un seul bloc alors qu'ils correspondent à plusieurs mots.

   | Sortie HTR | Correction |
   |---|---|
   | `justicemoyenne` | `justice moyenne` |
   | `bassesustce` | `basse justice` |
   | `lettrespatentes` | `lettres patentes` |
   | `procureurgeneral` | `procureur général` |
   | `foyethommage` | `foy et hommage` |

   Deux mécanismes sont utilisés :

   - règles fixes pour les expressions juridiques très sûres ;
   - segmentation automatique uniquement quand un token inconnu se décompose clairement en deux ou trois mots du lexique de référence.

   Cette correction est volontairement prudente : elle ne cherche pas à réécrire toute la ligne, seulement à restaurer des espaces quand le risque de surcorrection est faible.

3. Suggestions lexicales non appliquées automatiquement.

   Elles utilisent la distance de Levenshtein entre le token OCR et le lexique. Elles sont proposées dans le CSV pour aider la correction humaine, mais ne modifient pas automatiquement le texte.

Cette séparation évite de surcorriger des graphies anciennes ou des noms propres.

## Résultats actuels

Dernière exécution :

- lignes traitées : 247 ;
- suggestions proposées : 466 ;
- corrections appliquées automatiquement : 75 ;
- lignes modifiées : 53 ;
- formes uniques brutes : 912 ;
- formes uniques corrigées : 907 ;
- lignes avec référence manuelle : 100.

La dernière exécution corrige notamment :

- `justicemoyenne` -> `justice moyenne` ;
- `bassesustce` -> `basse justice` ;
- `presentmois` -> `present mois` ;
- `desparis` -> `des paris`.

## CER/WER avant et après

Le script calcule automatiquement :

- CER avant correction ;
- WER avant correction ;
- CER après correction ;
- WER après correction ;
- différence avant/après.

Ces scores ne sont calculables que pour les lignes où la colonne `reference` est remplie dans :

```text
data/judicial_gt/judicial_gt_annotation_with_draft.csv
```

Sur les 100 lignes judiciaires annotées, la dernière évaluation donne :

- CER avant : 0,1257 ;
- CER après : 0,1075 ;
- WER avant : 0,4515 ;
- WER après : 0,4011.
