
"""Image preprocessing for historical manuscript pages and line images."""

import argparse
import json
import sys
from pathlib import Path

import cv2
import yaml
from skimage.filters import threshold_sauvola
from jdeskew.estimator import get_angle
from jdeskew.utility import rotate

INPUT_DIR = Path("data/raw")
OUTPUT_DIR = Path("data/processed")
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)


DEFAULT_PARAMS = {
    "deskew": True,
    "clahe_clip_limit": 2.0,
    "clahe_tile_grid_size": [8, 8],
    "median_blur_kernel": 3,
    "sauvola_window_size": 25,
}


def load_preprocessing_params(config_path: str | Path = "config.yaml") -> dict:
    """Load reproducible preprocessing parameters from YAML.

    Args:
        config_path: Path to the project configuration.

    Returns:
        Parameter dictionary with defaults filled in.
    """
    params = dict(DEFAULT_PARAMS)
    path = Path(config_path)
    if path.exists():
        config = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        params.update(config.get("preprocessing", {}))
    return params


def preprocess_image(path, output_dir: Path = OUTPUT_DIR, params: dict | None = None):
    """Preprocess one manuscript image with deskew, CLAHE, blur, and Sauvola.

    Args:
        path: Input image path.
        output_dir: Directory where the processed binary image is written.
        params: Optional preprocessing parameter dictionary.

    Returns:
        Metadata describing the generated file and parameters.
    """
    params = dict(DEFAULT_PARAMS | (params or {}))
    image = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise FileNotFoundError(f"Could not read image: {path}")

    angle = 0.0
    if params.get("deskew", True):
        angle = float(get_angle(image))
        image = rotate(image, angle)

    tile_size = tuple(params.get("clahe_tile_grid_size", [8, 8]))
    clahe = cv2.createCLAHE(clipLimit=float(params.get("clahe_clip_limit", 2.0)), tileGridSize=tile_size)
    image = clahe.apply(image)

    blur_kernel = int(params.get("median_blur_kernel", 3))
    if blur_kernel > 1:
        image = cv2.medianBlur(image, blur_kernel)

    thresh = threshold_sauvola(image, window_size=int(params.get("sauvola_window_size", 25)))
    binary = (image > thresh).astype("uint8") * 255

    output_dir.mkdir(exist_ok=True, parents=True)
    out = output_dir / Path(path).name
    cv2.imwrite(str(out), binary)

    return {"input": str(path), "output": str(out), "deskew_angle": angle, "params": params}


def main() -> None:
    """Run preprocessing over an input directory."""
    parser = argparse.ArgumentParser(description="Preprocess manuscript images.")
    parser.add_argument("--config", default="config.yaml")
    parser.add_argument("--input-dir", default=str(INPUT_DIR))
    parser.add_argument("--output-dir", default=str(OUTPUT_DIR))
    args = parser.parse_args()

    params = load_preprocessing_params(args.config)
    reports = []
    for path in Path(args.input_dir).glob("*.png"):
        report = preprocess_image(path, Path(args.output_dir), params)
        reports.append(report)
        print(f"Processed {path.name}")
    print(json.dumps(reports, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
