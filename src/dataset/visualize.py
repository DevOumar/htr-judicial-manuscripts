import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt
from PIL import Image

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.dataset.load_dataset import load_configured_dataset
from src.utils.config import ensure_directories, load_config


def _to_pil(image_value) -> Image.Image:
    if isinstance(image_value, Image.Image):
        return image_value.convert("RGB")
    return Image.open(image_value).convert("RGB")


def save_sample_grid(config_path: str = "config.yaml", split: str = "train", count: int = 9) -> Path:
    config = load_config(config_path)
    ensure_directories(config)
    dataset = load_configured_dataset(config_path)

    if split not in dataset:
        raise ValueError(f"Split '{split}' not found. Available splits: {list(dataset.keys())}")

    samples = dataset[split].select(range(min(count, len(dataset[split]))))
    if len(samples) == 0:
        raise ValueError(f"Split '{split}' is empty after filtering.")

    columns = min(3, len(samples))
    rows = (len(samples) + columns - 1) // columns
    fig, axes = plt.subplots(rows, columns, figsize=(5 * columns, 4 * rows))
    axes_list = axes.flatten() if hasattr(axes, "flatten") else [axes]

    for axis in axes_list:
        axis.axis("off")

    for axis, sample in zip(axes_list, samples):
        image = _to_pil(sample["image"])
        axis.imshow(image)
        axis.set_title(sample["text"][:80], fontsize=9)

    output_dir = Path(config["paths"].get("samples_dir", "outputs/dataset_samples"))
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{split}_samples.png"
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Save a grid of dataset samples.")
    parser.add_argument("--config", default="config.yaml")
    parser.add_argument("--split", default="train")
    parser.add_argument("--count", type=int, default=9)
    args = parser.parse_args()

    output_path = save_sample_grid(args.config, args.split, args.count)
    print(f"Sample grid saved to {output_path}")


if __name__ == "__main__":
    main()
