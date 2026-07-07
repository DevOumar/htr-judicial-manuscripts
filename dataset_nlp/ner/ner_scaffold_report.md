# NER CamemBERT-LoRA : scaffold

- Modèle de départ : `Jean-Baptiste/camembert-ner`
- Nombre de labels : `11`
- Échantillon BIO : `data\ner\bio_sample.csv`
- Phrases annotées : `12`
- Tokens annotés : `224`

## Labels

`O`, `B-PER`, `I-PER`, `B-LOC`, `I-LOC`, `B-ORG`, `I-ORG`, `B-DATE`, `I-DATE`, `B-TITLE`, `I-TITLE`

## Alignement WordPiece

Les tokens spéciaux et les sous-tokens de continuation reçoivent `-100`.
Seul le premier sous-token porte le label BIO du mot original.

## Évaluation type seqeval

- F1 micro sur l'échantillon de contrôle : `1.0000`

## Limite

Ce scaffold valide le format, l'alignement et la métrique. Il ne remplace pas un fine-tuning long.
