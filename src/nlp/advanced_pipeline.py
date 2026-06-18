"""Lightweight advanced NLP pipeline for judicial HTR outputs.

This module covers the presentation requirements that do not need heavy model
training: BIO entities, heuristic POS tags, rule-based relations, graph export,
and TEI-XML. It is intentionally transparent and deterministic.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List
from xml.etree import ElementTree as ET

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.nlp.correction import correct_text, load_lexicon
from src.nlp.text_processing import TokenRecord, tokenize


ENTITY_LEXICON: Dict[str, str] = {
    "paris": "LOC",
    "picardie": "LOC",
    "corbeil": "LOC",
    "thionvilles": "LOC",
    "roy": "TITLE",
    "reine": "TITLE",
    "seigneur": "TITLE",
    "procureur": "TITLE",
    "president": "TITLE",
    "presidens": "TITLE",
    "parlement": "ORG",
    "cour": "ORG",
    "chambre": "ORG",
    "chambres": "ORG",
    "greffe": "ORG",
}

MONTHS = {
    "janvier",
    "fevrier",
    "mars",
    "avril",
    "may",
    "mai",
    "juin",
    "juillet",
    "aoust",
    "aout",
    "septembre",
    "octobre",
    "novembre",
    "decembre",
}

DETERMINERS = {"le", "la", "les", "un", "une", "du", "des", "de", "d", "l", "au", "aux", "ce", "cette"}
ADPOSITIONS = {"a", "de", "du", "en", "par", "pour", "sur", "sous", "avec", "sans", "devant"}
CONJUNCTIONS = {"et", "ou", "que", "qu", "comme"}
VERB_FORMS = {
    "dit",
    "demande",
    "donne",
    "ordonne",
    "proceder",
    "faire",
    "bailler",
    "assister",
    "relevera",
    "releveront",
    "appartiendra",
    "appartiendroit",
    "demandoit",
}


def pos_tag(token: TokenRecord) -> str:
    """Assign a simple Universal POS tag to one token."""
    norm = token.normalized
    if token.token_type == "number":
        return "NUM"
    if token.token_type == "punct":
        return "PUNCT"
    if norm in DETERMINERS:
        return "DET"
    if norm in ADPOSITIONS:
        return "ADP"
    if norm in CONJUNCTIONS:
        return "CCONJ"
    if norm in VERB_FORMS or norm.endswith(("oit", "oient", "er", "ir")):
        return "VERB"
    if token.text[:1].isupper() and len(token.text) > 1:
        return "PROPN"
    return "NOUN"


def bio_tag_tokens(tokens: List[TokenRecord]) -> List[Dict[str, Any]]:
    """Create token records with heuristic BIO entity labels and POS tags."""
    rows: List[Dict[str, Any]] = []
    previous_label = "O"
    for token in tokens:
        norm = token.normalized
        label = "O"
        if norm in ENTITY_LEXICON:
            label = ENTITY_LEXICON[norm]
        elif norm in MONTHS or re.fullmatch(r"1[5-7]\d\d", norm):
            label = "DATE"
        elif token.text[:1].isupper() and token.token_type == "word" and len(token.text) > 2:
            label = "PER"

        if label == "O":
            bio = "O"
            previous_label = "O"
        else:
            prefix = "I" if previous_label == label else "B"
            bio = f"{prefix}-{label}"
            previous_label = label

        rows.append(
            {
                "text": token.text,
                "normalized": token.normalized,
                "lemma": token.lemma,
                "pos": pos_tag(token),
                "bio": bio,
                "start": token.start,
                "end": token.end,
            }
        )
    return rows


def extract_entities(tagged_tokens: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Collapse BIO tokens into entity spans."""
    entities: List[Dict[str, Any]] = []
    current: Dict[str, Any] | None = None
    for token in tagged_tokens:
        bio = str(token["bio"])
        if bio == "O":
            if current:
                entities.append(current)
                current = None
            continue
        prefix, label = bio.split("-", 1)
        if prefix == "B" or not current or current["label"] != label:
            if current:
                entities.append(current)
            current = {
                "text": token["text"],
                "label": label,
                "start": token["start"],
                "end": token["end"],
            }
        else:
            current["text"] += " " + token["text"]
            current["end"] = token["end"]
    if current:
        entities.append(current)
    return entities


def extract_relations(entities: List[Dict[str, Any]], text: str) -> List[Dict[str, str]]:
    """Extract simple document relations from nearby entities."""
    relations: List[Dict[str, str]] = []
    titles = [item for item in entities if item["label"] == "TITLE"]
    locs = [item for item in entities if item["label"] == "LOC"]
    orgs = [item for item in entities if item["label"] == "ORG"]
    dates = [item for item in entities if item["label"] == "DATE"]

    for title in titles:
        for org in orgs:
            if abs(int(title["start"]) - int(org["start"])) < 120:
                relations.append({"source": title["text"], "target": org["text"], "type": "acts_in"})
    for org in orgs:
        for loc in locs:
            if abs(int(org["start"]) - int(loc["start"])) < 160:
                relations.append({"source": org["text"], "target": loc["text"], "type": "located_near"})
    if dates:
        first_date = dates[0]["text"]
        subject = orgs[0]["text"] if orgs else "document"
        relations.append({"source": subject, "target": first_date, "type": "dated"})
    if "justice moyenne" in text:
        relations.append({"source": "justice moyenne", "target": "Parlement de Paris", "type": "legal_topic"})
    if "basse justice" in text:
        relations.append({"source": "basse justice", "target": "Parlement de Paris", "type": "legal_topic"})
    return relations


def build_graph(entities: Iterable[Dict[str, Any]], relations: Iterable[Dict[str, str]]) -> Dict[str, Any]:
    """Build a serializable graph and optionally a NetworkX graph."""
    nodes: Dict[str, Dict[str, str]] = {}
    edges: List[Dict[str, str]] = []
    for entity in entities:
        text = str(entity["text"])
        nodes[text] = {"id": text, "label": str(entity["label"])}
    for relation in relations:
        source = relation["source"]
        target = relation["target"]
        nodes.setdefault(source, {"id": source, "label": "UNKNOWN"})
        nodes.setdefault(target, {"id": target, "label": "UNKNOWN"})
        edges.append({"source": source, "target": target, "type": relation["type"]})
    return {"nodes": sorted(nodes.values(), key=lambda item: item["id"]), "edges": edges}


def write_graphml(graph: Dict[str, Any], output_path: Path) -> None:
    """Write a small GraphML file without requiring NetworkX at runtime."""
    graphml = ET.Element("graphml", xmlns="http://graphml.graphdrawing.org/xmlns")
    graph_el = ET.SubElement(graphml, "graph", edgedefault="directed")
    for node in graph["nodes"]:
        node_el = ET.SubElement(graph_el, "node", id=node["id"])
        data = ET.SubElement(node_el, "data", key="label")
        data.text = node["label"]
    for index, edge in enumerate(graph["edges"]):
        edge_el = ET.SubElement(graph_el, "edge", id=f"e{index}", source=edge["source"], target=edge["target"])
        data = ET.SubElement(edge_el, "data", key="type")
        data.text = edge["type"]
    ET.ElementTree(graphml).write(output_path, encoding="utf-8", xml_declaration=True)


def write_tei(lines: List[Dict[str, Any]], output_path: Path) -> None:
    """Write a minimal TEI-XML transcription with entity tags."""
    tei = ET.Element("TEI")
    text_el = ET.SubElement(tei, "text")
    body = ET.SubElement(text_el, "body")
    for line in lines:
        line_el = ET.SubElement(body, "ab", {"xml:id": str(line.get("line_id", ""))})
        cursor = 0
        text = str(line["text"])
        for entity in line["entities"]:
            start = int(entity["start"])
            end = int(entity["end"])
            if start > cursor:
                if len(line_el):
                    line_el[-1].tail = (line_el[-1].tail or "") + text[cursor:start]
                else:
                    line_el.text = (line_el.text or "") + text[cursor:start]
            tag_by_label = {
                "PER": "persName",
                "LOC": "placeName",
                "DATE": "date",
                "ORG": "orgName",
                "TITLE": "roleName",
            }
            tag = tag_by_label.get(str(entity["label"]), "name")
            attrs = {"type": str(entity["label"]).lower()}
            ent_el = ET.SubElement(line_el, tag, attrs)
            ent_el.text = text[start:end]
            cursor = end
        remainder = text[cursor:]
        if len(line_el):
            line_el[-1].tail = (line_el[-1].tail or "") + remainder
        else:
            line_el.text = (line_el.text or "") + remainder
    ET.ElementTree(tei).write(output_path, encoding="utf-8", xml_declaration=True)


def run_advanced_nlp(
    input_path: str = "dataset_nlp/transcriptions.json",
    lexicon_path: str = "data/lexicons/judicial_lexicon.txt",
    output_dir: str = "dataset_nlp/advanced",
) -> Dict[str, Any]:
    """Run heuristic NER/POS/relation extraction and write presentation outputs."""
    rows = json.load(Path(input_path).open("r", encoding="utf-8"))
    lexicon = load_lexicon(lexicon_path)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    processed: List[Dict[str, Any]] = []
    all_entities: List[Dict[str, Any]] = []
    all_relations: List[Dict[str, str]] = []
    pos_counts: Counter[str] = Counter()
    bio_counts: Counter[str] = Counter()

    for row in rows:
        raw_text = str(row.get("transcription") or row.get("prediction") or "")
        corrected = correct_text(raw_text, lexicon)["corrected_text"]
        tokens = tokenize(corrected)
        tagged = bio_tag_tokens(tokens)
        entities = extract_entities(tagged)
        relations = extract_relations(entities, corrected)
        for token in tagged:
            pos_counts[token["pos"]] += 1
            bio_counts[token["bio"]] += 1
        for entity in entities:
            all_entities.append({"page_id": row.get("page_id"), "line_id": row.get("line_id"), **entity})
        all_relations.extend(relations)
        processed.append(
            {
                "page_id": row.get("page_id"),
                "line_id": row.get("line_id"),
                "order": row.get("order"),
                "text": corrected,
                "tokens": tagged,
                "entities": entities,
                "relations": relations,
            }
        )

    graph = build_graph(all_entities, all_relations)
    summary = {
        "input_path": input_path,
        "num_lines": len(processed),
        "num_entities": len(all_entities),
        "num_relations": len(all_relations),
        "entity_counts": dict(Counter(item["label"] for item in all_entities)),
        "pos_counts": dict(pos_counts),
        "bio_counts": dict(bio_counts),
        "outputs": {
            "annotated_json": str(output / "advanced_annotations.json"),
            "graph_json": str(output / "entity_graph.json"),
            "graphml": str(output / "entity_graph.graphml"),
            "tei": str(output / "transcription_tei.xml"),
            "report": str(output / "advanced_nlp_report.md"),
        },
        "limitations": [
            "NER is rule-based, not CamemBERT-LoRA fine-tuned.",
            "POS tags are heuristic fallback tags, not Stanza/Pie predictions.",
            "Relations are deterministic proximity/rule relations.",
        ],
    }

    (output / "advanced_annotations.json").write_text(json.dumps(processed, indent=2, ensure_ascii=False), encoding="utf-8")
    (output / "entity_graph.json").write_text(json.dumps(graph, indent=2, ensure_ascii=False), encoding="utf-8")
    write_graphml(graph, output / "entity_graph.graphml")
    write_tei(processed, output / "transcription_tei.xml")
    (output / "advanced_nlp_report.md").write_text(_report_markdown(summary), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return summary


def _report_markdown(summary: Dict[str, Any]) -> str:
    """Render the advanced NLP summary for the soutenance."""
    lines = [
        "# NLP avance : NER, POS, relations, graphe et TEI",
        "",
        "Cette sortie est une implementation legere et deterministe pour la soutenance.",
        "Elle ne pretend pas remplacer un fine-tuning CamemBERT-LoRA.",
        "",
        f"- Lignes traitees : {summary['num_lines']}",
        f"- Entites detectees : {summary['num_entities']}",
        f"- Relations extraites : {summary['num_relations']}",
        "",
        "## Entites BIO",
        "",
    ]
    for label, count in sorted(summary["entity_counts"].items()):
        lines.append(f"- `{label}` : {count}")
    lines.extend(["", "## POS", ""])
    for label, count in sorted(summary["pos_counts"].items()):
        lines.append(f"- `{label}` : {count}")
    lines.extend(["", "## Sorties", ""])
    for name, path in summary["outputs"].items():
        lines.append(f"- `{name}` : `{path}`")
    lines.extend(["", "## Limites honnetes", ""])
    for item in summary["limitations"]:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(description="Run lightweight advanced NLP on judicial HTR outputs.")
    parser.add_argument("--input", default="dataset_nlp/transcriptions.json")
    parser.add_argument("--lexicon", default="data/lexicons/judicial_lexicon.txt")
    parser.add_argument("--output-dir", default="dataset_nlp/advanced")
    args = parser.parse_args()
    run_advanced_nlp(args.input, args.lexicon, args.output_dir)


if __name__ == "__main__":
    main()
