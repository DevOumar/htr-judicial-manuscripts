# HTR Judicial Manuscripts

Pipeline de reconnaissance de texte manuscrit (HTR) pour manuscrits judiciaires francais anciens.

## Objectif
Construire un pipeline de bout en bout :
1. pretraitement des images,
2. segmentation,
3. reconnaissance HTR (TrOCR),
4. evaluation (CER/WER),
5. export des resultats (JSON, PAGE XML).

## Stack technique
- Python
- PyTorch
- Transformers (TrOCR)
- Kraken (segmentation, integration en cours)
- Outils evaluation: `jiwer`, `editdistance`

## Structure du projet
```text
htr-judicial-manuscripts/
|- src/
|  |- preprocessing/
|  |- segmentation/
|  |- htr/
|  |- evaluation/
|  |- export/
|  `- dataset/
|- tests/
|- data/
|- outputs/
|- notebooks/
|- experiments/
`- page_xml/
```

## Installation
Prerequis:
- Python 3.10+
- pip

Commandes:
```bash
python -m venv .venv
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Execution rapide
Pretraitement:
```bash
python src/preprocessing/preprocess.py
```

Entrainement (squelette actuel):
```bash
python src/htr/train_trocr.py
```

Inference:
```bash
python src/htr/inference.py
```

Evaluation:
```bash
python src/evaluation/evaluate.py
```

Export:
```bash
python src/export/export_json.py
python src/export/export_pagexml.py
```

## Dataset recommande
CATMuS Medieval:
https://huggingface.co/datasets/CATMuS/medieval

## Collaboration (universitaire)
- Branche principale: `main`
- Travailler par branches courtes (`feature/...`, `fix/...`)
- Commits atomiques et messages explicites
- Pull Request avec description claire et impact sur les experiences

## Bonnes pratiques Git
- Ne pas versionner les donnees brutes, checkpoints, caches, outputs locaux
- Ne jamais versionner de secrets (`.env` exclu)
- Garder les scripts reproductibles et documenter les commandes utilisees

## Etat actuel
Ce repository contient une base fonctionnelle de pipeline avec plusieurs modules encore en cours d'integration (notamment la segmentation Kraken et l'entrainement reel TrOCR).
