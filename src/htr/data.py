from dataclasses import dataclass
from typing import Any, Dict, List

import torch
from PIL import Image


def to_rgb_image(image_value: Any) -> Image.Image:
    if isinstance(image_value, Image.Image):
        return image_value.convert("RGB")
    return Image.open(image_value).convert("RGB")


def encode_trocr_batch(batch: Dict[str, List[Any]], processor: Any, max_target_length: int) -> Dict[str, Any]:
    images = [to_rgb_image(image) for image in batch["image"]]
    pixel_values = processor(images=images, return_tensors="pt").pixel_values
    labels = processor.tokenizer(
        batch["text"],
        padding="max_length",
        max_length=max_target_length,
        truncation=True,
    ).input_ids

    labels = [
        [(token if token != processor.tokenizer.pad_token_id else -100) for token in label]
        for label in labels
    ]

    return {"pixel_values": pixel_values.numpy(), "labels": labels}


@dataclass
class TrOCRDataCollator:
    processor: Any

    def __call__(self, features: List[Dict[str, Any]]) -> Dict[str, torch.Tensor]:
        pixel_values = torch.stack([torch.as_tensor(feature["pixel_values"]) for feature in features])
        labels = torch.stack([torch.as_tensor(feature["labels"], dtype=torch.long) for feature in features])
        return {"pixel_values": pixel_values, "labels": labels}
