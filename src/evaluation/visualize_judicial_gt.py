"""Generate an HTML transcription aid for selected judicial line crops."""

from __future__ import annotations

import argparse
import base64
import csv
import html
from pathlib import Path
from typing import Dict, List


def _image_data_uri(path: str) -> str:
    image_path = Path(path)
    data = base64.b64encode(image_path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{data}"


def load_rows(csv_path: str) -> List[Dict[str, str]]:
    """Load selected ground-truth rows from CSV."""
    return list(csv.DictReader(Path(csv_path).open("r", encoding="utf-8")))


def write_html(
    csv_path: str = "data/judicial_gt/judicial_gt_template.csv",
    output_path: str = "data/judicial_gt/judicial_gt_viewer.html",
) -> None:
    """Write a self-contained HTML viewer for manual transcription.

    Args:
        csv_path: Ground-truth template CSV.
        output_path: HTML destination.
    """
    rows = load_rows(csv_path)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    parts = [
        "<!doctype html>",
        "<html><head><meta charset='utf-8'>",
        "<title>Judicial Ground Truth Viewer</title>",
        "<style>",
        "body{font-family:Arial,sans-serif;margin:24px;background:#f7f7f7;color:#111}",
        ".row{background:white;border:1px solid #ddd;margin:12px 0;padding:12px;border-radius:6px}",
        "img{display:block;max-width:100%;height:auto;image-rendering:auto;border:1px solid #ccc;background:white}",
        "textarea{width:100%;min-height:54px;margin-top:8px;font-size:16px;font-family:serif}",
        ".meta{font-size:13px;color:#555;margin-bottom:6px}",
        "code{background:#eee;padding:2px 4px;border-radius:3px}",
        "</style></head><body>",
        "<h1>Judicial Ground Truth Viewer</h1>",
        "<p>Transcrire manuellement chaque ligne dans le CSV <code>judicial_gt_template.csv</code>. Les zones de texte ci-dessous servent uniquement d'aide visuelle.</p>",
    ]
    for index, row in enumerate(rows, start=1):
        crop_path = row["crop_path"]
        reference = html.escape(row.get("reference", ""))
        parts.extend(
            [
                "<div class='row'>",
                f"<div class='meta'>#{index} | page: <code>{html.escape(row['page_id'])}</code> | line: <code>{html.escape(row['line_id'])}</code> | crop: <code>{html.escape(crop_path)}</code></div>",
                f"<img src='{_image_data_uri(crop_path)}' alt='line crop {index}'>",
                f"<textarea placeholder='Transcription manuelle'>{reference}</textarea>",
                "</div>",
            ]
        )
    parts.append("</body></html>")
    output.write_text("\n".join(parts), encoding="utf-8")
    print(str(output))


def main() -> None:
    """Run HTML viewer generation from the command line."""
    parser = argparse.ArgumentParser(description="Generate an HTML viewer for judicial GT transcription.")
    parser.add_argument("--csv", default="data/judicial_gt/judicial_gt_template.csv")
    parser.add_argument("--output", default="data/judicial_gt/judicial_gt_viewer.html")
    args = parser.parse_args()
    write_html(args.csv, args.output)


if __name__ == "__main__":
    main()
