# NER CamemBERT-LoRA : scaffold

- Modele de depart : `Jean-Baptiste/camembert-ner`
- Nombre de labels : `11`
- Echantillon BIO : `data\ner\bio_sample.csv`
- Phrases annotees : `12`
- Tokens annotés : `224`

## Labels

`O`, `B-PER`, `I-PER`, `B-LOC`, `I-LOC`, `B-ORG`, `I-ORG`, `B-DATE`, `I-DATE`, `B-TITLE`, `I-TITLE`

## Alignement WordPiece

Les tokens speciaux et les sous-tokens de continuation recoivent `-100`.
Seul le premier sous-token porte le label BIO du mot original.

## Evaluation type seqeval

- F1 micro sur l'echantillon de controle : `1.0000`

## Limite

Ce scaffold valide le format, l'alignement et la metrique. Il ne remplace pas un fine-tuning long.
