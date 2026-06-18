import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

import torch
from tqdm import tqdm
from transformers import TrOCRProcessor, VisionEncoderDecoderModel

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.dataset.load_dataset import load_configured_dataset
from src.htr.data import to_rgb_image
from src.htr.metrics import average_cer, cer, corpus_wer
from src.utils.config import ensure_directories, load_config


def predict_text(
    image_value: Any,
    processor: TrOCRProcessor,
    model: VisionEncoderDecoderModel,
    device: torch.device,
    max_length: int,
) -> str:
    image = to_rgb_image(image_value)
    pixel_values = processor(images=image, return_tensors="pt").pixel_values.to(device)

    with torch.no_grad():
        generated_ids = model.generate(pixel_values, max_length=max_length)

    return processor.batch_decode(generated_ids, skip_special_tokens=True)[0]


def evaluate(
    config_path: str = "config.yaml",
    model_path: str | None = None,
    split: str = "test",
    output_name: str | None = None,
) -> Dict[str, Any]:
    config = load_config(config_path)
    ensure_directories(config)

    model_dir = model_path or str(Path(config["model"]["output_dir"]) / "final")
    max_length = config["training"].get("generation_max_length", 128)
    output_dir = Path(config["paths"].get("evaluation_dir", "outputs/evaluation"))
    output_dir.mkdir(parents=True, exist_ok=True)

    dataset = load_configured_dataset(config_path)
    if split not in dataset:
        raise ValueError(f"Split '{split}' not found. Available splits: {list(dataset.keys())}")
    eval_dataset = dataset[split]
    max_samples = config.get("evaluation", {}).get("max_samples")
    if max_samples and len(eval_dataset) > max_samples:
        eval_dataset = eval_dataset.select(range(max_samples))

    processor_source = model_dir
    if not (Path(model_dir) / "preprocessor_config.json").exists():
        processor_source = config["model"]["name"]

    processor = TrOCRProcessor.from_pretrained(processor_source)
    model = VisionEncoderDecoderModel.from_pretrained(model_dir)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()

    rows: List[Dict[str, Any]] = []
    references: List[str] = []
    predictions: List[str] = []

    for sample in tqdm(eval_dataset, desc=f"Evaluating {split}"):
        reference = sample["text"]
        prediction = predict_text(sample["image"], processor, model, device, max_length)
        sample_cer = cer(reference, prediction)

        rows.append(
            {
                "sample_id": sample.get("sample_id", ""),
                "reference": reference,
                "prediction": prediction,
                "cer": sample_cer,
                "reference_length": len(reference),
                "prediction_length": len(prediction),
            }
        )
        references.append(reference)
        predictions.append(prediction)

    metrics = {
        "split": split,
        "model_path": model_dir,
        "num_samples": len(rows),
        "cer": average_cer(references, predictions),
        "wer": corpus_wer(references, predictions),
    }

    prefix = output_name or split
    predictions_path = output_dir / f"{prefix}_predictions.csv"
    with predictions_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()) if rows else [])
        if rows:
            writer.writeheader()
            writer.writerows(rows)

    metrics_path = output_dir / f"{prefix}_metrics.json"
    with metrics_path.open("w", encoding="utf-8") as handle:
        json.dump(metrics, handle, indent=2, ensure_ascii=False)

    examples_path = output_dir / f"{prefix}_prediction_examples.json"
    examples = sorted(rows, key=lambda row: row["cer"], reverse=True)[:10]
    with examples_path.open("w", encoding="utf-8") as handle:
        json.dump(examples, handle, indent=2, ensure_ascii=False)

    print(f"Metrics saved to {metrics_path}")
    print(f"Predictions saved to {predictions_path}")
    print(metrics)
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate a trained TrOCR model.")
    parser.add_argument("--config", default="config.yaml")
    parser.add_argument("--model-path", default=None)
    parser.add_argument("--split", default="test")
    parser.add_argument("--output-name", default=None)
    args = parser.parse_args()
    evaluate(args.config, args.model_path, args.split, args.output_name)


if __name__ == "__main__":
    main()
