import argparse
import csv
import json
import re
import sys
from pathlib import Path
from statistics import mean, median
from typing import Any, Dict, List

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[2]))


REPEATED_CHAR_RE = re.compile(r"(.)\1{3,}")


def _prediction_flags(text: str) -> Dict[str, Any]:
    stripped = text.strip()
    chars = [char for char in stripped if not char.isspace()]
    unique_ratio = len(set(chars)) / len(chars) if chars else 0.0
    repeated_runs = REPEATED_CHAR_RE.findall(stripped)
    tokens = stripped.split()
    repeated_tokens = sum(1 for left, right in zip(tokens, tokens[1:]) if left == right)
    return {
        "prediction_length": len(stripped),
        "token_count": len(tokens),
        "unique_char_ratio": unique_ratio,
        "repeated_char_run_count": len(repeated_runs),
        "repeated_adjacent_token_count": repeated_tokens,
        "empty_prediction": not stripped,
        "suspicious_prediction": (
            not stripped
            or len(stripped) < 3
            or len(repeated_runs) > 0
            or repeated_tokens > 0
            or (len(chars) >= 8 and unique_ratio < 0.35)
        ),
    }


def _crop_metrics(crop_path: Path) -> Dict[str, float]:
    with Image.open(crop_path).convert("L") as image:
        array = np.asarray(image, dtype=np.float32)
        width, height = image.size
    return {
        "width": float(width),
        "height": float(height),
        "contrast": float(array.std()),
        "mean_gray": float(array.mean()),
        "dark_pixel_ratio": float((array < 180).mean()),
    }


def _stats(values: List[float]) -> Dict[str, float]:
    if not values:
        return {"mean": 0.0, "median": 0.0}
    return {"mean": float(mean(values)), "median": float(median(values))}


def analyze_directory(input_dir: str = "outputs/judicial_demo", output_dir: str = "outputs/htr_analysis") -> Dict[str, Any]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

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
            prediction = line.get("prediction", "") or ""
            row = {
                "page": page_dir.name,
                "order": line.get("order"),
                "id": line.get("id"),
                "crop_path": str(crop_path),
                "prediction": prediction,
            }
            row.update(_crop_metrics(crop_path))
            row.update(_prediction_flags(prediction))
            rows.append(row)

    suspicious = [row for row in rows if row["suspicious_prediction"]]
    lengths = [row["prediction_length"] for row in rows]
    contrasts = [row["contrast"] for row in rows]
    heights = [row["height"] for row in rows]

    report = {
        "input_dir": input_dir,
        "num_lines": len(rows),
        "suspicious_prediction_count": len(suspicious),
        "empty_prediction_count": sum(1 for row in rows if row["empty_prediction"]),
        "repeated_char_run_count": sum(1 for row in rows if row["repeated_char_run_count"]),
        "repeated_adjacent_token_count": sum(1 for row in rows if row["repeated_adjacent_token_count"]),
        "prediction_length": _stats(lengths),
        "crop_contrast": _stats(contrasts),
        "crop_height": _stats(heights),
        "main_failure_hypotheses": [
            "Le modele TrOCR local reste insuffisamment adapte aux ecritures judiciaires du XVIIe siecle.",
            "Les crops sont parfois tres longs et peu contrastes, ce qui amplifie les repetitions de caracteres.",
            "Le modele a ete entraine/evalue sur CATMuS mais le domaine Parlement de Paris presente un decalage d'ecriture, langue et mise en page.",
            "Sans ground truth judiciaire, les mesures CER/WER directes sur Gallica ne sont pas possibles; le diagnostic utilise donc des heuristiques de lisibilite.",
        ],
        "suspicious_examples": suspicious[:30],
    }

    with (output / "htr_failure_report.json").open("w", encoding="utf-8") as handle:
        json.dump({"summary": report, "lines": rows}, handle, indent=2, ensure_ascii=False)

    with (output / "suspicious_examples.csv").open("w", encoding="utf-8", newline="") as handle:
        fieldnames = list(rows[0].keys()) if rows else ["page"]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(suspicious)

    if rows:
        fig, axis = plt.subplots(figsize=(7, 5))
        axis.scatter(contrasts, lengths, s=12)
        axis.set_xlabel("crop contrast")
        axis.set_ylabel("prediction length")
        axis.set_title("Prediction length vs crop contrast")
        fig.tight_layout()
        fig.savefig(output / "prediction_length_vs_contrast.png", dpi=150)
        plt.close(fig)

    with (output / "htr_failure_report.md").open("w", encoding="utf-8") as handle:
        handle.write("# HTR failure analysis\n\n")
        handle.write(f"- Lines analyzed: {report['num_lines']}\n")
        handle.write(f"- Suspicious predictions: {report['suspicious_prediction_count']}\n")
        handle.write(f"- Empty predictions: {report['empty_prediction_count']}\n")
        handle.write(f"- Lines with repeated character runs: {report['repeated_char_run_count']}\n")
        handle.write(f"- Prediction length mean/median: {report['prediction_length']['mean']:.1f} / {report['prediction_length']['median']:.1f}\n")
        handle.write(f"- Crop contrast mean/median: {report['crop_contrast']['mean']:.1f} / {report['crop_contrast']['median']:.1f}\n\n")
        handle.write("## Diagnosis\n\n")
        for hypothesis in report["main_failure_hypotheses"]:
            handle.write(f"- {hypothesis}\n")
        handle.write("\nSee `suspicious_examples.csv` and `prediction_length_vs_contrast.png`.\n")

    print(json.dumps(report, indent=2, ensure_ascii=False))
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze likely HTR failure modes on judicial line predictions.")
    parser.add_argument("--input-dir", default="outputs/judicial_demo")
    parser.add_argument("--output-dir", default="outputs/htr_analysis")
    args = parser.parse_args()
    analyze_directory(args.input_dir, args.output_dir)


if __name__ == "__main__":
    main()
