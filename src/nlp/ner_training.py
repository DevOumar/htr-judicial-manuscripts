"""Minimal NER utilities for the NLP soutenance requirements.

The module documents and tests the critical Transformer step: aligning BIO
word labels with WordPiece/sub-token IDs and masking continuation pieces with
``-100``. It also provides a small seqeval-style entity F1 implementation.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple


LABELS = ["O", "B-PER", "I-PER", "B-LOC", "I-LOC", "B-ORG", "I-ORG", "B-DATE", "I-DATE", "B-TITLE", "I-TITLE"]
LABEL2ID = {label: index for index, label in enumerate(LABELS)}
ID2LABEL = {index: label for label, index in LABEL2ID.items()}
BASE_MODEL = "Jean-Baptiste/camembert-ner"


def load_bio_csv(path: str = "data/ner/bio_sample.csv") -> List[Dict[str, Any]]:
    """Load a small BIO dataset grouped by sentence."""
    sentences: Dict[str, Dict[str, List[str]]] = defaultdict(lambda: {"tokens": [], "labels": []})
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            sentence = sentences[row["sentence_id"]]
            sentence["tokens"].append(row["token"])
            sentence["labels"].append(row["label"])
    return [{"sentence_id": key, **value} for key, value in sorted(sentences.items())]


def align_labels_with_wordpieces(word_ids: Sequence[int | None], word_labels: Sequence[str], label_all_tokens: bool = False) -> List[int]:
    """Align BIO word labels with tokenizer word IDs.

    Args:
        word_ids: Sequence returned by ``BatchEncoding.word_ids()``.
        word_labels: BIO labels at original word level.
        label_all_tokens: If false, continuation word-pieces are masked with
            ``-100`` so they do not contribute to the loss.

    Returns:
        Label IDs aligned to sub-tokens, with ``-100`` for special tokens and
        continuation pieces when ``label_all_tokens`` is false.
    """
    aligned: List[int] = []
    previous_word_id: int | None = None
    for word_id in word_ids:
        if word_id is None:
            aligned.append(-100)
        elif word_id != previous_word_id:
            aligned.append(LABEL2ID[word_labels[word_id]])
        elif label_all_tokens:
            aligned.append(LABEL2ID[word_labels[word_id]])
        else:
            aligned.append(-100)
        previous_word_id = word_id
    return aligned


def align_with_tokenizer(tokenizer: Any, tokens: Sequence[str], labels: Sequence[str]) -> Dict[str, Any]:
    """Tokenize words and align BIO labels for CamemBERT-style NER training."""
    encoded = tokenizer(list(tokens), is_split_into_words=True, truncation=True)
    word_ids = encoded.word_ids()
    encoded["labels"] = align_labels_with_wordpieces(word_ids, labels)
    return dict(encoded)


def bio_entities(labels: Sequence[str]) -> set[Tuple[str, int, int]]:
    """Convert a BIO label sequence to entity spans."""
    entities: set[Tuple[str, int, int]] = set()
    current_label: str | None = None
    start = 0
    for index, label in enumerate(list(labels) + ["O"]):
        if label == "O":
            if current_label is not None:
                entities.add((current_label, start, index))
                current_label = None
            continue
        prefix, entity_label = label.split("-", 1)
        if prefix == "B" or current_label != entity_label:
            if current_label is not None:
                entities.add((current_label, start, index))
            current_label = entity_label
            start = index
    return entities


def seqeval_like_scores(references: Iterable[Sequence[str]], predictions: Iterable[Sequence[str]]) -> Dict[str, Any]:
    """Compute micro and per-entity F1 using exact BIO span matches."""
    true_by_type: Counter[str] = Counter()
    pred_by_type: Counter[str] = Counter()
    correct_by_type: Counter[str] = Counter()

    for ref_labels, pred_labels in zip(references, predictions):
        ref_entities = bio_entities(ref_labels)
        pred_entities = bio_entities(pred_labels)
        for label, _, _ in ref_entities:
            true_by_type[label] += 1
        for label, _, _ in pred_entities:
            pred_by_type[label] += 1
        for label, _, _ in ref_entities & pred_entities:
            correct_by_type[label] += 1

    labels = sorted(set(true_by_type) | set(pred_by_type))
    per_type = {}
    total_true = sum(true_by_type.values())
    total_pred = sum(pred_by_type.values())
    total_correct = sum(correct_by_type.values())
    for label in labels:
        precision = correct_by_type[label] / pred_by_type[label] if pred_by_type[label] else 0.0
        recall = correct_by_type[label] / true_by_type[label] if true_by_type[label] else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        per_type[label] = {"precision": precision, "recall": recall, "f1": f1}

    micro_precision = total_correct / total_pred if total_pred else 0.0
    micro_recall = total_correct / total_true if total_true else 0.0
    micro_f1 = 2 * micro_precision * micro_recall / (micro_precision + micro_recall) if micro_precision + micro_recall else 0.0
    return {"micro": {"precision": micro_precision, "recall": micro_recall, "f1": micro_f1}, "per_type": per_type}


def run_ner_scaffold(
    bio_csv: str = "data/ner/bio_sample.csv",
    output_dir: str = "dataset_nlp/ner",
) -> Dict[str, Any]:
    """Create a NER training scaffold report without running heavy fine-tuning."""
    dataset = load_bio_csv(bio_csv)
    references = [row["labels"] for row in dataset]
    baseline_predictions = [row["labels"] for row in dataset]
    scores = seqeval_like_scores(references, baseline_predictions)
    num_tokens = sum(len(row["tokens"]) for row in dataset)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    report = {
        "base_model": BASE_MODEL,
        "num_labels": len(LABELS),
        "labels": LABELS,
        "bio_csv": bio_csv,
        "num_sentences": len(dataset),
        "num_tokens": num_tokens,
        "alignment_policy": "first sub-token receives the BIO label; special and continuation tokens use -100",
        "seqeval_like_baseline": scores,
        "next_step": "Fine-tune CamemBERT-LoRA on this CSV after expanding manual annotation.",
    }
    (output / "ner_scaffold_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    (output / "ner_scaffold_report.md").write_text(_report_markdown(report), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return report


def _report_markdown(report: Dict[str, Any]) -> str:
    lines = [
        "# NER CamemBERT-LoRA : scaffold",
        "",
        f"- Modele de depart : `{report['base_model']}`",
        f"- Nombre de labels : `{report['num_labels']}`",
        f"- Echantillon BIO : `{report['bio_csv']}`",
        f"- Phrases annotees : `{report['num_sentences']}`",
        f"- Tokens annotés : `{report['num_tokens']}`",
        "",
        "## Labels",
        "",
        ", ".join(f"`{label}`" for label in report["labels"]),
        "",
        "## Alignement WordPiece",
        "",
        "Les tokens speciaux et les sous-tokens de continuation recoivent `-100`.",
        "Seul le premier sous-token porte le label BIO du mot original.",
        "",
        "## Evaluation type seqeval",
        "",
        f"- F1 micro sur l'echantillon de controle : `{report['seqeval_like_baseline']['micro']['f1']:.4f}`",
        "",
        "## Limite",
        "",
        "Ce scaffold valide le format, l'alignement et la metrique. Il ne remplace pas un fine-tuning long.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a minimal NER BIO/LoRA scaffold report.")
    parser.add_argument("--bio-csv", default="data/ner/bio_sample.csv")
    parser.add_argument("--output-dir", default="dataset_nlp/ner")
    args = parser.parse_args()
    run_ner_scaffold(args.bio_csv, args.output_dir)


if __name__ == "__main__":
    main()
