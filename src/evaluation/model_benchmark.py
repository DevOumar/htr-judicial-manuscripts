import argparse
import csv
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

import torch
from PIL import Image
from transformers import TrOCRProcessor, VisionEncoderDecoderModel

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[2]))


CATMUS_METRIC_FILES = {
    "microsoft/trocr-small-handwritten": "outputs/evaluation/baseline_french_metrics.json",
    "dj0w/trocr-french-handwriting-v5": "outputs/evaluation/trocr_french_v5_metrics.json",
    "models/trocr-catmus-french-decoder/final": "outputs/evaluation/french_decoder_metrics.json",
}


def _rss_mb() -> float | None:
    try:
        import psutil
    except ImportError:
        return None
    return psutil.Process().memory_info().rss / (1024 * 1024)


def _load_catmus_metrics(model_id: str) -> Dict[str, Any]:
    configured_path = CATMUS_METRIC_FILES.get(model_id)
    if not configured_path:
        return {"cer": None, "wer": None, "source": None}
    metric_path = Path(configured_path)
    if not metric_path.exists():
        return {"cer": None, "wer": None, "source": None}
    data = json.load(metric_path.open("r", encoding="utf-8"))
    return {"cer": data.get("cer"), "wer": data.get("wer"), "source": str(metric_path)}


def _line_crops(input_dir: str, max_lines: int) -> List[Path]:
    crops: List[Path] = []
    for page_dir in sorted(Path(input_dir).glob("page_*_canvas_*")):
        for crop_path in sorted((page_dir / "lines").glob("*.png")):
            crops.append(crop_path)
            if len(crops) >= max_lines:
                return crops
    return crops


def _predict_model(model_id: str, crops: List[Path], max_length: int, num_beams: int) -> Dict[str, Any]:
    start_memory = _rss_mb()
    start = time.perf_counter()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    processor = TrOCRProcessor.from_pretrained(model_id, local_files_only=True)
    model = VisionEncoderDecoderModel.from_pretrained(model_id, local_files_only=True)
    model.to(device)
    model.eval()

    predictions = []
    line_times = []
    for crop_path in crops:
        line_start = time.perf_counter()
        image = Image.open(crop_path).convert("RGB")
        pixel_values = processor(images=image, return_tensors="pt").pixel_values.to(device)
        with torch.no_grad():
            generated_ids = model.generate(pixel_values, max_length=max_length, num_beams=num_beams)
        prediction = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        elapsed = time.perf_counter() - line_start
        line_times.append(elapsed)
        predictions.append({"crop_path": str(crop_path), "prediction": prediction, "seconds": elapsed})

    total_seconds = time.perf_counter() - start
    end_memory = _rss_mb()
    memory_delta = None
    if start_memory is not None and end_memory is not None:
        memory_delta = max(0.0, end_memory - start_memory)

    return {
        "status": "ok",
        "num_lines": len(crops),
        "total_seconds": total_seconds,
        "average_seconds_per_line": total_seconds / len(crops) if crops else 0.0,
        "memory_delta_mb": memory_delta,
        "device": str(device),
        "predictions": predictions,
    }


def benchmark_models(
    input_dir: str = "outputs/judicial_demo",
    output_dir: str = "outputs/model_benchmark",
    max_lines: int = 5,
    include_base: bool = False,
    include_large: bool = False,
) -> Dict[str, Any]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    models = [
        "microsoft/trocr-small-handwritten",
        "dj0w/trocr-french-handwriting-v5",
        "models/trocr-catmus-french-decoder/final",
    ]
    if include_base:
        models.append("microsoft/trocr-base-handwritten")
    skipped = [
        {
            "model": "johnlockejrr/pylaia_catmus_medieval",
            "reason": "Skipped: PyLaia model is not directly loadable with Transformers TrOCR classes in this environment.",
        }
    ]
    if include_large:
        models.append("microsoft/trocr-large-handwritten")
    else:
        skipped.append(
            {
                "model": "microsoft/trocr-large-handwritten",
                "reason": "Skipped by default because it is heavy for CPU; pass --include-large for an explicit run.",
            }
        )

    crops = _line_crops(input_dir, max_lines)
    results = []
    prediction_rows = []
    for model_id in models:
        catmus = _load_catmus_metrics(model_id)
        try:
            runtime = _predict_model(model_id, crops, max_length=96, num_beams=1)
        except Exception as exc:
            runtime = {
                "status": "failed",
                "error": str(exc),
                "predictions": [],
                "note": "Model was attempted in local cache mode only to keep the benchmark reproducible without network access.",
            }
        for prediction in runtime.get("predictions", []):
            prediction_rows.append({"model": model_id, **prediction})
        results.append({"model": model_id, "catmus_metrics": catmus, "judicial_runtime": runtime})

    report = {
        "input_dir": input_dir,
        "max_lines": max_lines,
        "num_judicial_lines": len(crops),
        "models": results,
        "skipped_models": skipped,
        "notes": [
            "CER/WER are available only when ground truth exists. The judicial Gallica pages have no line-level ground truth, so the benchmark reports runtime and qualitative predictions on the same judicial crops.",
            "CATMuS CER/WER values are reused from prior evaluations when their metric files are present.",
            "Model loading uses local_files_only=True. Missing models are reported as unavailable instead of downloading during validation.",
        ],
    }

    with (output / "model_benchmark_report.json").open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, ensure_ascii=False)

    with (output / "judicial_predictions.csv").open("w", encoding="utf-8", newline="") as handle:
        fieldnames = list(prediction_rows[0].keys()) if prediction_rows else ["model"]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(prediction_rows)

    with (output / "model_benchmark_report.md").open("w", encoding="utf-8") as handle:
        handle.write("# Model benchmark\n\n")
        handle.write(f"- Judicial crops used for runtime/qualitative comparison: {len(crops)}\n\n")
        handle.write("| Model | CATMuS CER | CATMuS WER | Status | Avg sec/line | Memory delta MB |\n")
        handle.write("| --- | ---: | ---: | --- | ---: | ---: |\n")
        for item in results:
            metrics = item["catmus_metrics"]
            runtime = item["judicial_runtime"]
            handle.write(
                f"| {item['model']} | {metrics.get('cer')} | {metrics.get('wer')} | "
                f"{runtime.get('status')} | {runtime.get('average_seconds_per_line')} | {runtime.get('memory_delta_mb')} |\n"
            )
        if skipped:
            handle.write("\n## Skipped models\n\n")
            for item in skipped:
                handle.write(f"- {item['model']}: {item['reason']}\n")

    print(json.dumps({k: v for k, v in report.items() if k != "models"}, indent=2, ensure_ascii=False))
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark HTR models on the same judicial line crops.")
    parser.add_argument("--input-dir", default="outputs/judicial_demo")
    parser.add_argument("--output-dir", default="outputs/model_benchmark")
    parser.add_argument("--max-lines", type=int, default=5)
    parser.add_argument("--include-base", action="store_true")
    parser.add_argument("--include-large", action="store_true")
    args = parser.parse_args()
    benchmark_models(args.input_dir, args.output_dir, args.max_lines, args.include_base, args.include_large)


if __name__ == "__main__":
    main()
