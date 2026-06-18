import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

import requests
from PIL import Image

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.segmentation.kraken_segmentation import segment_page_with_config
from src.utils.config import load_config


USER_AGENT = "htr-judicial-manuscripts/0.1"


def fetch_manifest(manifest_url: str) -> Dict[str, Any]:
    response = requests.get(manifest_url, timeout=120, headers={"User-Agent": USER_AGENT})
    response.raise_for_status()
    return response.json()


def canvas_image_url(canvas: Dict[str, Any], image_width: int | None = None) -> str:
    resource = canvas["images"][0]["resource"]
    service = resource.get("service", {})
    service_id = service.get("@id")
    if service_id and image_width:
        return f"{service_id}/full/{image_width},/0/native.jpg"
    return resource["@id"]


def download_page(canvas: Dict[str, Any], output_path: Path, image_width: int | None = None) -> Dict[str, Any]:
    resource = canvas["images"][0]["resource"]
    candidates = [canvas_image_url(canvas, image_width), resource["@id"]]
    response = None
    url = candidates[0]
    for candidate in dict.fromkeys(candidates):
        url = candidate
        response = requests.get(candidate, timeout=180, headers={"User-Agent": USER_AGENT})
        if response.status_code == 200:
            break
    if response is None:
        raise RuntimeError("No image request was attempted.")
    response.raise_for_status()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(response.content)

    with Image.open(output_path) as image:
        size = image.size

    return {
        "label": canvas.get("label"),
        "iiif_url": url,
        "width": size[0],
        "height": size[1],
        "path": str(output_path),
    }


def run_judicial_demo(config_path: str = "config.yaml") -> Dict[str, Any]:
    config = load_config(config_path)
    demo_config = config.get("judicial_demo", {})
    output_dir = Path(demo_config.get("output_dir", "outputs/judicial_demo"))
    pages_dir = output_dir / "pages_original"
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest = fetch_manifest(demo_config["manifest_url"])
    canvases = manifest["sequences"][0]["canvases"]
    page_indices = [int(value) for value in demo_config.get("page_indices", [20, 21, 22, 23, 24])]
    image_width = demo_config.get("image_width", 1600)
    should_transcribe = bool(demo_config.get("transcribe", True))
    configured_max_transcribed = demo_config.get("max_transcribed_lines_per_page")
    max_transcribed = int(configured_max_transcribed) if configured_max_transcribed is not None else None

    pages: List[Dict[str, Any]] = []
    page_number = 1
    attempted_indices = list(page_indices)
    next_index = max(attempted_indices) + 1 if attempted_indices else 0

    while len(pages) < len(page_indices) and attempted_indices:
        canvas_index = attempted_indices.pop(0)
        if canvas_index < 0 or canvas_index >= len(canvases):
            raise IndexError(f"Canvas index {canvas_index} is outside manifest range 0..{len(canvases) - 1}.")

        page_id = f"page_{page_number:02d}_canvas_{canvas_index + 1:04d}"
        page_image_path = pages_dir / f"{page_id}.jpg"
        try:
            download_info = download_page(canvases[canvas_index], page_image_path, image_width)
        except requests.HTTPError as exc:
            if next_index < len(canvases):
                attempted_indices.append(next_index)
                next_index += 1
                print(f"Skipping canvas {canvas_index + 1}: {exc}")
                continue
            raise

        page_output_dir = output_dir / page_id
        summary = segment_page_with_config(
            config=config,
            output_dir=page_output_dir,
            image_path=str(page_image_path),
            transcribe=should_transcribe,
            max_transcribed_lines=max_transcribed,
        )

        pages.append(
            {
                "page_id": page_id,
                "canvas_index": canvas_index,
                "canvas_label": download_info.get("label"),
                "download": download_info,
                "pipeline": summary,
            }
        )
        page_number += 1

    total_lines = sum(page["pipeline"].get("num_lines", 0) for page in pages)
    total_transcribed = sum(page["pipeline"].get("num_transcribed_lines", 0) for page in pages)
    total_seconds = sum(page["pipeline"].get("transcription", {}).get("total_seconds", 0.0) for page in pages)

    report = {
        "corpus": {
            "name": demo_config.get("corpus_name"),
            "institution": demo_config.get("institution"),
            "ark": demo_config.get("ark"),
            "source_url": demo_config.get("source_url"),
            "manifest_url": demo_config.get("manifest_url"),
            "period": demo_config.get("period"),
            "description": demo_config.get("description"),
            "license": "Gallica conditions of use",
        },
        "num_pages": len(pages),
        "total_lines": total_lines,
        "total_transcribed_lines": total_transcribed,
        "total_transcription_seconds": total_seconds,
        "average_seconds_per_line": total_seconds / total_transcribed if total_transcribed else 0.0,
        "pages": pages,
    }

    report_path = output_dir / "demo_report.json"
    with report_path.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, ensure_ascii=False)

    print(json.dumps({"output_dir": str(output_dir), "report": str(report_path), "num_pages": len(pages)}, indent=2))
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the judicial manuscript demo on Gallica pages.")
    parser.add_argument("--config", default="config.yaml")
    args = parser.parse_args()
    run_judicial_demo(args.config)


if __name__ == "__main__":
    main()
