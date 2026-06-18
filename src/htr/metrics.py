from typing import Iterable, List

import editdistance
from jiwer import wer


def cer(reference: str, hypothesis: str) -> float:
    return editdistance.eval(reference, hypothesis) / max(len(reference), 1)


def average_cer(references: Iterable[str], hypotheses: Iterable[str]) -> float:
    scores = [cer(reference, hypothesis) for reference, hypothesis in zip(references, hypotheses)]
    return sum(scores) / max(len(scores), 1)


def corpus_wer(references: List[str], hypotheses: List[str]) -> float:
    if not references:
        return 0.0
    return wer(references, hypotheses)
