"""Create a representative manual transcription template for judicial line crops."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

from PIL import Image

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[2]))


def _line_width(line: Dict[str, Any]) -> int:
    bbox = line.get("bbox") or [0, 0, 0, 0]
    return int(bbox[2] - bbox[0])


def _line_height(line: Dict[str, Any]) -> int:
    bbox = line.get("bbox") or [0, 0, 0, 0]
    return int(bbox[3] - bbox[1])


def collect_lines(input_dir: str = "outputs/judicial_demo") -> List[Dict[str, Any]]:
    """Collect all line records from judicial demo outputs.

    Args:
        input_dir: Directory containing `page_*_canvas_*` outputs.

    Returns:
        List of line dictionaries enriched with page identifiers and dimensions.
    """
    rows: List[Dict[str, Any]] = []
    for page_dir in sorted(Path(input_dir).glob("page_*_canvas_*")):
        transcriptions_path = page_dir / "transcriptions.json"
        if not transcriptions_path.exists():
            continue
        lines = json.load(transcriptions_path.open("r", encoding="utf-8"))
        for line in lines:
            crop_path = Path(line.get("crop_path", ""))
            if not crop_path.exists():
                continue
            with Image.open(crop_path) as image:
                crop_width, crop_height = image.size
            rows.append(
                {
                    "page_id": page_dir.name,
                    "line_id": line.get("line_id") or line.get("id"),
                    "order": int(line.get("order", 0)),
                    "crop_path": str(crop_path),
                    "prediction": line.get("prediction", ""),
                    "confidence": line.get("confidence"),
                    "needs_review": line.get("needs_review"),
                    "bbox_width": _line_width(line) or crop_width,
                    "bbox_height": _line_height(line) or crop_height,
                    "crop_width": crop_width,
                    "crop_height": crop_height,
                }
            )
    return rows


def select_representative_lines(lines: List[Dict[str, Any]], target_count: int = 100) -> List[Dict[str, Any]]:
    """Select representative lines across pages, columns, and crop sizes.

    The selection is deterministic. It first removes very tiny fragments, then
    samples evenly per page and across reading order while preserving difficult
    low-confidence examples.

    Args:
        lines: Candidate line rows.
        target_count: Number of lines to select.

    Returns:
        Selected line rows sorted by page and reading order.
    """
    eligible = [row for row in lines if row["crop_width"] >= 80 and row["crop_height"] >= 20]
    if len(eligible) < target_count:
        eligible = list(lines)

    by_page: Dict[str, List[Dict[str, Any]]] = {}
    for row in eligible:
        by_page.setdefault(row["page_id"], []).append(row)

    selected: List[Dict[str, Any]] = []
    per_page = max(1, target_count // max(len(by_page), 1))
    remainder = target_count - per_page * len(by_page)

    for page_index, page_id in enumerate(sorted(by_page)):
        page_rows = sorted(by_page[page_id], key=lambda row: row["order"])
        count = per_page + (1 if page_index < remainder else 0)
        if len(page_rows) <= count:
            selected.extend(page_rows)
            continue
        step = (len(page_rows) - 1) / max(count - 1, 1)
        indices = sorted({round(i * step) for i in range(count)})
        selected.extend(page_rows[index] for index in indices[:count])

    selected_ids = {(row["page_id"], row["line_id"]) for row in selected}
    difficult = sorted(
        eligible,
        key=lambda row: (
            row.get("needs_review") is not True,
            float(row.get("confidence") or 1.0),
            -row["crop_width"],
        ),
    )
    for row in difficult:
        if len(selected) >= target_count:
            break
        key = (row["page_id"], row["line_id"])
        if key not in selected_ids:
            selected.append(row)
            selected_ids.add(key)

    return sorted(selected[:target_count], key=lambda row: (row["page_id"], row["order"]))


def write_template(
    input_dir: str = "outputs/judicial_demo",
    output_path: str = "data/judicial_gt/judicial_gt_template.csv",
    target_count: int = 100,
) -> Dict[str, Any]:
    """Create the judicial ground-truth CSV template.

    Args:
        input_dir: Judicial demo outputs.
        output_path: Destination CSV path.
        target_count: Number of representative lines.

    Returns:
        Summary dictionary.
    """
    lines = collect_lines(input_dir)
    selected = select_representative_lines(lines, target_count)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["page_id", "line_id", "crop_path", "reference"])
        writer.writeheader()
        for row in selected:
            writer.writerow(
                {
                    "page_id": row["page_id"],
                    "line_id": row["line_id"],
                    "crop_path": row["crop_path"],
                    "reference": "",
                }
            )
    summary = {
        "input_dir": input_dir,
        "output_path": str(output),
        "available_lines": len(lines),
        "selected_lines": len(selected),
        "pages": sorted({row["page_id"] for row in selected}),
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return summary


def main() -> None:
    """Run template creation from the command line."""
    parser = argparse.ArgumentParser(description="Create a judicial ground-truth transcription CSV template.")
    parser.add_argument("--input-dir", default="outputs/judicial_demo")
    parser.add_argument("--output", default="data/judicial_gt/judicial_gt_template.csv")
    parser.add_argument("--count", type=int, default=100)
    args = parser.parse_args()
    write_template(args.input_dir, args.output, args.count)


if __name__ == "__main__":
    main()
