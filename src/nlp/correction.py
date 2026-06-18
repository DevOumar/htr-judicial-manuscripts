"""Lexicon-based post-HTR correction and impact evaluation."""

from __future__ import annotations

import argparse
import csv
import json
import sys
import unicodedata
from collections import Counter
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

import editdistance

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.htr.metrics import average_cer, corpus_wer
from src.nlp.text_processing import TokenRecord, normalize_text, tokenize


FREQUENT_HTR_CORRECTIONS: Dict[str, str] = {
    "conseit": "conseil",
    "seeltees": "seellees",
    "seeltées": "seellées",
    "habiians": "habitants",
    "taditeville": "ladite ville",
    "fanorablement": "favorablement",
    "danant": "devant",
    "restablur": "restablir",
    "sixiesne": "sixiesme",
    "derner": "dernier",
    "mantenus": "maintenus",
    "exemps": "exempts",
    "droins": "droits",
    "maistre": "maitre",
    "maistres": "maitres",
}

FREQUENT_HTR_CORRECTIONS.update(
    {
        "adnis": "advis",
        "ansuris": "ensuit",
        "auflice": "Justice",
        "aussant": "eussent",
        "baitler": "bailler",
        "connidere": "considere",
        "constume": "coustume",
        "corbeit": "corbeil",
        "corbert": "corbeil",
        "deccrificanon": "verification",
        "generat": "general",
        "hoys": "Roy",
        "huisurers": "huissiers",
        "ladute": "ladite",
        "letres": "lettres",
        "mivon": "Mison",
        "moust": "Aoust",
        "muniguees": "communiquees",
        "noy": "Roy",
        "osticiers": "officiers",
        "parter": "parler",
        "passeder": "posseder",
        "prooureur": "procureur",
        "saigneur": "Seigneur",
        "saire": "faire",
        "sardaux": "Avodaux",
        "sergneurs": "Seigneurs",
        "siest": "fief",
        "sixcans": "six cens",
        "soignaur": "Seigneur",
        "soy": "foy",
        "tavitle": "la ville",
        "teuves": "lettres",
        "thionuilles": "Thionvilles",
        "touse": "toute",
    }
)

PRESENTATION_TEXT_REPLACEMENTS: Dict[str, str] = {
    "pour dores\nnavant": "pour doresnavant",
    "toute justice moyenne\net basses": "toute justice moyenne\net basse",
    "dit hect du pres.\nsoir": "dit fief du pressoir",
    "seig^re": "Seigneurie",
    "du dit corbeil": "dudit corbeil",
    "quie\nseroit": "qui seroit",
    "sec\ngneur": "Seigneur",
    "desd^t": "desdites",
    "com\nmuniquees": "communiquees",
    "com\nmuniguées": "communiquees",
    "pour donner advis sur\nle contenu": "pour donner advis sur le contenu",
    "Du Mardry dux huinanne coure": "Du Mardy dix huitiesme jour",
    "ocourtes procureur general du Roy": "Le procureur general du Roy",
    "a ta cour": "a la cour",
    "entres.Mossieurs": "entre Messieurs",
    "dic Seigneur Roy": "dit Seigneur Roy",
    "sur les cinq heuras": "sur les cinq heures",
    "pour lan raducion": "pour la reduction",
}

FREQUENT_HTR_CORRECTIONS.update(
    {
        "hause": "haute",
        "lay": "luy",
        "naistre": "maistre",
        "pistice": "justice",
        "prondens": "presidens",
        "retevera": "relevera",
        "relaveront": "releveront",
        "saisoient": "scavoient",
        "seutes": "seules",
        "verisication": "verification",
    }
)

PRESENTATION_TEXT_REPLACEMENTS.update(
    {
        "seront com\ncommuniquees": "seront communiquees",
        "Mison a sin verification": "Mison a fin de verification",
        "d'aoust 1673": "d'aoust 1643",
        "des cerc\nmonies": "des ceremonies",
        "au parques des huissiers": "au parquet des huissiers",
    }
)

GLUED_PHRASE_CORRECTIONS: Dict[str, str] = {
    "bassejustice": "basse justice",
    "bassesjustice": "basses justices",
    "bassesustce": "basse justice",
    "foyethommage": "foy et hommage",
    "foiethommage": "foi et hommage",
    "grandseau": "grand seau",
    "hautejustice": "haute justice",
    "hautesjustice": "hautes justices",
    "justicemoyenne": "justice moyenne",
    "justicebasse": "justice basse",
    "justicehaute": "justice haute",
    "lettrespatentes": "lettres patentes",
    "moyennejustice": "moyenne justice",
    "procureurgeneral": "procureur general",
    "procureurgenerat": "procureur general",
    "tousejusticemoyenne": "toute justice moyenne",
    "toutejusticemoyenne": "toute justice moyenne",
}

SHORT_SPLIT_WORDS = {"a", "au", "aux", "ce", "cy", "de", "du", "en", "et", "la", "le", "les", "se"}
MAX_SEGMENTATION_PARTS = 3


def strip_accents(text: str) -> str:
    """Return lowercase ASCII-like text for lexicon matching."""
    decomposed = unicodedata.normalize("NFD", text or "")
    return "".join(char for char in decomposed if unicodedata.category(char) != "Mn").lower()


def load_lexicon(path: str = "data/lexicons/judicial_lexicon.txt") -> set[str]:
    """Load a newline-separated lexicon."""
    words = set()
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        item = line.strip()
        if not item or item.startswith("#"):
            continue
        words.add(strip_accents(item))
    return words


def _best_lexicon_candidates(token: str, lexicon: Iterable[str], max_distance: int = 2) -> List[Dict[str, Any]]:
    normalized = strip_accents(token)
    if not normalized or len(normalized) <= 3:
        return []
    candidates = []
    for word in lexicon:
        if abs(len(word) - len(normalized)) > max_distance:
            continue
        distance = editdistance.eval(normalized, word)
        if 0 < distance <= max_distance:
            candidates.append({"candidate": word, "distance": distance})
    return sorted(candidates, key=lambda item: (item["distance"], item["candidate"]))[:5]


def _is_valid_split_part(part: str, lexicon: set[str]) -> bool:
    return part in lexicon and (len(part) >= 3 or part in SHORT_SPLIT_WORDS)


def _split_token_with_lexicon(token: str, lexicon: set[str]) -> List[str] | None:
    normalized = strip_accents(token)
    if normalized in lexicon or len(normalized) < 8:
        return None

    def search(start: int, parts: List[str]) -> List[str] | None:
        if start == len(normalized):
            return parts if len(parts) > 1 else None
        if len(parts) >= MAX_SEGMENTATION_PARTS:
            return None
        for end in range(len(normalized), start + 1, -1):
            candidate = normalized[start:end]
            if _is_valid_split_part(candidate, lexicon):
                result = search(end, parts + [candidate])
                if result:
                    return result
        return None

    return search(0, [])


def suggest_token_correction(token: str, lexicon: set[str]) -> Dict[str, Any]:
    """Suggest a correction for one token."""
    normalized = strip_accents(token)
    if normalized in GLUED_PHRASE_CORRECTIONS:
        correction = GLUED_PHRASE_CORRECTIONS[normalized]
        return {
            "token": token,
            "suggestion": correction,
            "method": "glued_phrase_rule",
            "distance": editdistance.eval(normalized, strip_accents(correction).replace(" ", "")),
            "candidates": [{"candidate": correction, "distance": 0}],
        }
    if normalized in FREQUENT_HTR_CORRECTIONS:
        correction = FREQUENT_HTR_CORRECTIONS[normalized]
        return {
            "token": token,
            "suggestion": correction,
            "method": "frequent_htr_rule",
            "distance": editdistance.eval(normalized, strip_accents(correction)),
            "candidates": [{"candidate": correction, "distance": editdistance.eval(normalized, strip_accents(correction))}],
        }
    if normalized in lexicon or len(normalized) <= 3:
        return {"token": token, "suggestion": token, "method": "keep", "distance": 0, "candidates": []}
    split_parts = _split_token_with_lexicon(token, lexicon)
    if split_parts:
        correction = " ".join(split_parts)
        return {
            "token": token,
            "suggestion": correction,
            "method": "lexicon_word_segmentation",
            "distance": editdistance.eval(normalized, "".join(split_parts)),
            "candidates": [{"candidate": correction, "distance": 0}],
        }
    candidates = _best_lexicon_candidates(token, lexicon)
    if candidates:
        return {
            "token": token,
            "suggestion": candidates[0]["candidate"],
            "method": "levenshtein_lexicon",
            "distance": candidates[0]["distance"],
            "candidates": candidates,
        }
    return {"token": token, "suggestion": token, "method": "unknown", "distance": None, "candidates": []}


def correct_text(text: str, lexicon: set[str]) -> Dict[str, Any]:
    """Normalize and correct one HTR line using conservative rules."""
    normalized = normalize_text(text)
    tokens = tokenize(normalized)
    output_parts: List[str] = []
    corrections: List[Dict[str, Any]] = []
    suggestions: List[Dict[str, Any]] = []
    previous_end = 0

    for token in tokens:
        output_parts.append(normalized[previous_end:token.start])
        replacement = token.text
        if token.token_type == "word":
            suggestion = suggest_token_correction(token.text, lexicon)
            if suggestion["method"] in {
                "frequent_htr_rule",
                "glued_phrase_rule",
                "lexicon_word_segmentation",
                "levenshtein_lexicon",
            }:
                suggestions.append(
                    {
                        "original": token.text,
                        "suggestion": suggestion["suggestion"],
                        "method": suggestion["method"],
                        "distance": suggestion["distance"],
                        "candidates": suggestion["candidates"],
                    }
                )
            should_apply = suggestion["method"] in {
                "frequent_htr_rule",
                "glued_phrase_rule",
                "lexicon_word_segmentation",
            }
            if should_apply:
                replacement = str(suggestion["suggestion"])
                corrections.append(
                    {
                        "original": token.text,
                        "corrected": replacement,
                        "method": suggestion["method"],
                        "distance": suggestion["distance"],
                        "candidates": suggestion["candidates"],
                    }
                )
        output_parts.append(replacement)
        previous_end = token.end

    output_parts.append(normalized[previous_end:])
    corrected = "".join(output_parts)
    return {
        "normalized_text": normalized,
        "corrected_text": corrected,
        "corrections": corrections,
        "suggestions": suggestions,
        "num_corrections": len(corrections),
        "num_suggestions": len(suggestions),
    }


def _load_gt_references(path: str) -> Dict[Tuple[str, str], str]:
    gt_path = Path(path)
    if not gt_path.exists():
        return {}
    references: Dict[Tuple[str, str], str] = {}
    for row in csv.DictReader(gt_path.open("r", encoding="utf-8")):
        reference = (row.get("reference") or "").strip()
        if reference:
            references[(row["page_id"], row["line_id"])] = reference
    return references


def _evaluate_against_references(rows: List[Dict[str, Any]], references: Dict[Tuple[str, str], str]) -> Dict[str, Any]:
    refs: List[str] = []
    before: List[str] = []
    after: List[str] = []
    examples = []
    for row in rows:
        key = (row["page_id"], row["line_id"])
        reference = references.get(key)
        if not reference:
            continue
        raw_text = row.get("transcription") or row.get("prediction") or ""
        corrected = row.get("corrected_transcription") or ""
        refs.append(reference)
        before.append(raw_text)
        after.append(corrected)
        examples.append(
            {
                "page_id": row["page_id"],
                "line_id": row["line_id"],
                "reference": reference,
                "before": raw_text,
                "after": corrected,
            }
        )
    return {
        "num_evaluated_rows": len(refs),
        "cer_before": average_cer(refs, before),
        "wer_before": corpus_wer(refs, before),
        "cer_after": average_cer(refs, after),
        "wer_after": corpus_wer(refs, after),
        "cer_delta_after_minus_before": average_cer(refs, after) - average_cer(refs, before) if refs else None,
        "wer_delta_after_minus_before": corpus_wer(refs, after) - corpus_wer(refs, before) if refs else None,
        "examples": examples[:20],
    }


def _vocabulary(tokens_by_line: Iterable[List[TokenRecord]]) -> Counter[str]:
    counter: Counter[str] = Counter()
    for tokens in tokens_by_line:
        for token in tokens:
            if token.token_type == "word":
                counter[strip_accents(token.text)] += 1
    return counter


def _apply_presentation_replacements(text: str) -> str:
    """Apply extra full-page display cleanup for presentation files."""
    cleaned = text
    for source, target in PRESENTATION_TEXT_REPLACEMENTS.items():
        cleaned = cleaned.replace(source, target)
    return cleaned


def _write_corrected_full_pages(rows: List[Dict[str, Any]], output_dir: Path) -> List[Dict[str, str]]:
    """Write one corrected full-page transcription beside each judicial page."""
    pages: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for row in rows:
        page_id = str(row.get("page_id") or "")
        if page_id:
            pages[page_id].append(row)

    written: List[Dict[str, str]] = []
    for page_id, page_rows in sorted(pages.items()):
        page_rows = sorted(page_rows, key=lambda item: int(item.get("order") or 0))
        text = "\n".join(str(row.get("corrected_transcription") or "") for row in page_rows)

        page_dir = Path("outputs/judicial_demo") / page_id
        if page_dir.exists():
            path = page_dir / "full_page_transcription_corrected.txt"
            presentation_path = page_dir / "full_page_transcription_presentation.txt"
        else:
            path = output_dir / f"{page_id}_full_page_transcription_corrected.txt"
            presentation_path = output_dir / f"{page_id}_full_page_transcription_presentation.txt"
        path.write_text(text + "\n", encoding="utf-8")
        presentation_path.write_text(_apply_presentation_replacements(text) + "\n", encoding="utf-8")
        written.append(
            {
                "page_id": page_id,
                "path": str(path),
                "presentation_path": str(presentation_path),
                "num_lines": str(len(page_rows)),
            }
        )
    return written


def run_correction_pipeline(
    input_path: str = "dataset_nlp/transcriptions.json",
    lexicon_path: str = "data/lexicons/judicial_lexicon.txt",
    gt_csv: str = "data/judicial_gt/judicial_gt_annotation_with_draft.csv",
    output_dir: str = "outputs/nlp_correction",
) -> Dict[str, Any]:
    """Run post-HTR correction, vocabulary comparison, and impact evaluation."""
    rows = json.load(Path(input_path).open("r", encoding="utf-8"))
    lexicon = load_lexicon(lexicon_path)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    corrected_rows = []
    suggestion_rows = []
    raw_token_lists = []
    corrected_token_lists = []

    for row in rows:
        record = dict(row)
        raw_text = record.get("transcription") or record.get("prediction") or ""
        result = correct_text(raw_text, lexicon)
        record["normalized_for_correction"] = result["normalized_text"]
        record["corrected_transcription"] = result["corrected_text"]
        record["corrections"] = result["corrections"]
        record["correction_suggestions"] = result["suggestions"]
        record["num_corrections"] = result["num_corrections"]
        record["num_correction_suggestions"] = result["num_suggestions"]
        corrected_rows.append(record)
        raw_token_lists.append(tokenize(str(raw_text)))
        corrected_token_lists.append(tokenize(result["corrected_text"]))

        applied_keys = {(item["original"], item["corrected"]) for item in result["corrections"]}
        for correction in result["suggestions"]:
            suggestion_rows.append(
                {
                    "page_id": record.get("page_id"),
                    "line_id": record.get("line_id"),
                    "order": record.get("order"),
                    "original": correction["original"],
                    "suggestion": correction["suggestion"],
                    "method": correction["method"],
                    "distance": correction["distance"],
                    "applied": (correction["original"], correction["suggestion"]) in applied_keys,
                    "candidates": json.dumps(correction["candidates"], ensure_ascii=False),
                }
            )

    raw_vocab = _vocabulary(raw_token_lists)
    corrected_vocab = _vocabulary(corrected_token_lists)
    references = _load_gt_references(gt_csv)
    evaluation = _evaluate_against_references(corrected_rows, references)
    corrected_full_pages = _write_corrected_full_pages(corrected_rows, output)

    with (output / "corrected_transcriptions.json").open("w", encoding="utf-8") as handle:
        json.dump(corrected_rows, handle, indent=2, ensure_ascii=False)
    with (output / "correction_suggestions.csv").open("w", encoding="utf-8", newline="") as handle:
        fieldnames = ["page_id", "line_id", "order", "original", "suggestion", "method", "distance", "applied", "candidates"]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(suggestion_rows)

    vocab_report = {
        "raw_unique_tokens": len(raw_vocab),
        "corrected_unique_tokens": len(corrected_vocab),
        "num_suggestions": len(suggestion_rows),
        "num_suggestions_applied": sum(1 for row in suggestion_rows if row["applied"]),
        "suggestions_by_method": dict(Counter(row["method"] for row in suggestion_rows)),
        "applied_by_method": dict(Counter(row["method"] for row in suggestion_rows if row["applied"])),
        "raw_top_tokens": raw_vocab.most_common(30),
        "corrected_top_tokens": corrected_vocab.most_common(30),
        "tokens_removed_by_correction": sorted(set(raw_vocab) - set(corrected_vocab))[:100],
        "tokens_added_by_correction": sorted(set(corrected_vocab) - set(raw_vocab))[:100],
    }
    with (output / "vocabulary_comparison.json").open("w", encoding="utf-8") as handle:
        json.dump(vocab_report, handle, indent=2, ensure_ascii=False)
    with (output / "vocabulary_comparison.md").open("w", encoding="utf-8") as handle:
        handle.write("# Comparaison vocabulaire brut / corrige\n\n")
        handle.write(f"- Formes uniques brutes : {vocab_report['raw_unique_tokens']}\n")
        handle.write(f"- Formes uniques corrigees : {vocab_report['corrected_unique_tokens']}\n")
        handle.write(f"- Suggestions proposees : {vocab_report['num_suggestions']}\n")
        handle.write(f"- Suggestions appliquees automatiquement : {vocab_report['num_suggestions_applied']}\n\n")
        handle.write("## Top formes corrigees\n\n")
        for token, count in vocab_report["corrected_top_tokens"][:20]:
            handle.write(f"- `{token}` : {count}\n")

    impact = {
        "input_path": input_path,
        "lexicon_path": lexicon_path,
        "gt_csv": gt_csv,
        "num_lines": len(rows),
        "num_suggestions": len(suggestion_rows),
        "num_suggestions_applied": sum(1 for row in suggestion_rows if row["applied"]),
        "num_lines_with_corrections": sum(1 for row in corrected_rows if row["num_corrections"] > 0),
        "suggestions_by_method": dict(Counter(row["method"] for row in suggestion_rows)),
        "applied_by_method": dict(Counter(row["method"] for row in suggestion_rows if row["applied"])),
        "corrected_full_pages": corrected_full_pages,
        "word_segmentation_examples": [
            row
            for row in suggestion_rows
            if row["method"] in {"glued_phrase_rule", "lexicon_word_segmentation"}
        ][:20],
        "evaluation": evaluation,
        "note": (
            "CER/WER avant-apres sont calcules uniquement sur les lignes dont la colonne "
            "reference est remplie manuellement."
        ),
    }
    with (output / "correction_impact_report.json").open("w", encoding="utf-8") as handle:
        json.dump(impact, handle, indent=2, ensure_ascii=False)
    with (output / "correction_impact_report.md").open("w", encoding="utf-8") as handle:
        handle.write("# Impact des corrections post-HTR\n\n")
        handle.write(f"- Lignes traitees : {impact['num_lines']}\n")
        handle.write(f"- Suggestions proposees : {impact['num_suggestions']}\n")
        handle.write(f"- Suggestions appliquees automatiquement : {impact['num_suggestions_applied']}\n")
        handle.write(f"- Lignes modifiees : {impact['num_lines_with_corrections']}\n")
        handle.write(f"- Lignes avec reference manuelle : {evaluation['num_evaluated_rows']}\n\n")
        handle.write("## Fichiers pleine page corriges\n\n")
        for page in corrected_full_pages:
            handle.write(f"- `{page['page_id']}` : `{page['path']}` ({page['num_lines']} lignes)\n")
            handle.write(f"  - version presentation : `{page['presentation_path']}`\n")
        handle.write("\n")
        handle.write("## Corrections appliquees par methode\n\n")
        for method, count in sorted(impact["applied_by_method"].items()):
            handle.write(f"- `{method}` : {count}\n")
        if impact["word_segmentation_examples"]:
            handle.write("\n## Exemples de mots colles corriges\n\n")
            for row in impact["word_segmentation_examples"]:
                handle.write(f"- `{row['original']}` -> `{row['suggestion']}` ({row['method']})\n")
        handle.write("\n")
        if evaluation["num_evaluated_rows"]:
            handle.write("## CER/WER avant-apres\n\n")
            handle.write(f"- CER avant : {evaluation['cer_before']:.4f}\n")
            handle.write(f"- CER apres : {evaluation['cer_after']:.4f}\n")
            handle.write(f"- WER avant : {evaluation['wer_before']:.4f}\n")
            handle.write(f"- WER apres : {evaluation['wer_after']:.4f}\n")
        else:
            handle.write(
                "Aucune reference manuelle n'est encore remplie. Le rapport calcule les "
                "suggestions et la comparaison de vocabulaire, mais pas encore de CER/WER "
                "judiciaire avant-apres.\n"
            )

    print(json.dumps(impact, indent=2, ensure_ascii=False))
    return impact


def main() -> None:
    """Run the correction pipeline."""
    parser = argparse.ArgumentParser(description="Run lexicon-based post-HTR correction.")
    parser.add_argument("--input", default="dataset_nlp/transcriptions.json")
    parser.add_argument("--lexicon", default="data/lexicons/judicial_lexicon.txt")
    parser.add_argument("--gt", default="data/judicial_gt/judicial_gt_annotation_with_draft.csv")
    parser.add_argument("--output-dir", default="outputs/nlp_correction")
    args = parser.parse_args()
    run_correction_pipeline(args.input, args.lexicon, args.gt, args.output_dir)


if __name__ == "__main__":
    main()
