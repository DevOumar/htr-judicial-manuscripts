import argparse
import csv
import sys
from pathlib import Path

import torch
from PIL import Image
from transformers import TrOCRProcessor, VisionEncoderDecoderModel

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[2]))


def collect_crops(root: Path, max_pages: int, max_lines_per_page: int) -> list[Path]:
    crops = []
    page_dirs = sorted(root.glob("page_*_canvas_*"))[:max_pages]
    for page_dir in page_dirs:
        line_paths = sorted((page_dir / "lines").glob("*.png"))[:max_lines_per_page]
        crops.extend(line_paths)
    return crops


def predict(model_path: str, crops_root: str, output_csv: str, max_pages: int = 5, max_lines_per_page: int = 1) -> Path:
    crop_paths = collect_crops(Path(crops_root), max_pages, max_lines_per_page)
    processor = TrOCRProcessor.from_pretrained(model_path)
    model = VisionEncoderDecoderModel.from_pretrained(model_path)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()

    rows = []
    for path in crop_paths:
        image = Image.open(path).convert("RGB")
        pixel_values = processor(images=image, return_tensors="pt").pixel_values.to(device)
        with torch.no_grad():
            generated_ids = model.generate(pixel_values, max_length=128, num_beams=1)
        text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        rows.append(
            {
                "page": path.parents[1].name,
                "line_image": str(path),
                "model": model_path,
                "prediction": text,
            }
        )

    output_path = Path(output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["page", "line_image", "model", "prediction"])
        writer.writeheader()
        writer.writerows(rows)

    print(output_path)
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Run TrOCR predictions on existing segmented line crops.")
    parser.add_argument("--model-path", required=True)
    parser.add_argument("--crops-root", default="outputs/judicial_demo")
    parser.add_argument("--output-csv", required=True)
    parser.add_argument("--max-pages", type=int, default=5)
    parser.add_argument("--max-lines-per-page", type=int, default=1)
    args = parser.parse_args()
    predict(args.model_path, args.crops_root, args.output_csv, args.max_pages, args.max_lines_per_page)


if __name__ == "__main__":
    main()
