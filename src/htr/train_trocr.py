import argparse
import inspect
import json
import sys
from pathlib import Path
from typing import Any, Dict

import numpy as np
from transformers import (
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
    TrOCRProcessor,
    VisionEncoderDecoderModel,
    set_seed,
)

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.dataset.load_dataset import load_configured_dataset
from src.htr.data import TrOCRDataCollator, encode_trocr_batch
from src.htr.metrics import average_cer, corpus_wer
from src.utils.config import ensure_directories, load_config


def configure_model(
    model: VisionEncoderDecoderModel,
    processor: TrOCRProcessor,
    max_length: int,
    num_beams: int,
) -> None:
    model.config.decoder_start_token_id = processor.tokenizer.cls_token_id
    model.config.pad_token_id = processor.tokenizer.pad_token_id
    model.config.vocab_size = model.config.decoder.vocab_size
    model.config.eos_token_id = processor.tokenizer.sep_token_id
    model.config.max_length = max_length
    model.config.num_beams = num_beams
    model.generation_config.max_length = max_length
    model.generation_config.num_beams = num_beams
    if num_beams > 1:
        model.config.early_stopping = True
        model.config.no_repeat_ngram_size = 3
        model.config.length_penalty = 2.0
        model.generation_config.early_stopping = True
        model.generation_config.no_repeat_ngram_size = 3
        model.generation_config.length_penalty = 2.0
    else:
        model.config.early_stopping = False
        model.config.no_repeat_ngram_size = 0
        model.config.length_penalty = 1.0
        model.generation_config.early_stopping = False
        model.generation_config.no_repeat_ngram_size = 0
        model.generation_config.length_penalty = 1.0


def apply_freezing(model: VisionEncoderDecoderModel, config: Dict[str, Any]) -> None:
    if config["training"].get("freeze_encoder", False):
        for parameter in model.encoder.parameters():
            parameter.requires_grad = False
        print("Encoder frozen: training decoder parameters only.")


def build_compute_metrics(processor: TrOCRProcessor):
    def compute_metrics(pred: Any) -> Dict[str, float]:
        label_ids = pred.label_ids.copy()
        label_ids[label_ids == -100] = processor.tokenizer.pad_token_id

        pred_ids = pred.predictions
        if isinstance(pred_ids, tuple):
            pred_ids = pred_ids[0]

        pred_texts = processor.batch_decode(pred_ids, skip_special_tokens=True)
        label_texts = processor.batch_decode(label_ids, skip_special_tokens=True)

        return {
            "cer": average_cer(label_texts, pred_texts),
            "wer": corpus_wer(label_texts, pred_texts),
        }

    return compute_metrics


def prepare_dataset(config_path: str, processor: TrOCRProcessor):
    config = load_config(config_path)
    max_length = config["training"].get("generation_max_length", 128)
    dataset = load_configured_dataset(config_path)

    def encode(batch: Dict[str, Any]) -> Dict[str, Any]:
        return encode_trocr_batch(batch, processor, max_length)

    encoded = dataset.map(
        encode,
        batched=True,
        remove_columns=dataset["train"].column_names,
        desc="Encoding dataset for TrOCR",
    )
    encoded.set_format(type="torch", columns=["pixel_values", "labels"])
    return encoded


def train(config_path: str = "config.yaml") -> Dict[str, Any]:
    config = load_config(config_path)
    ensure_directories(config)
    set_seed(config["training"].get("seed", 42))

    model_name = config["model"]["name"]
    output_dir = Path(config["model"]["output_dir"])
    max_length = config["training"].get("generation_max_length", 128)
    num_beams = config["training"].get("generation_num_beams", 1)

    processor = TrOCRProcessor.from_pretrained(model_name)
    model = VisionEncoderDecoderModel.from_pretrained(model_name)
    configure_model(model, processor, max_length, num_beams)
    apply_freezing(model, config)

    encoded_dataset = prepare_dataset(config_path, processor)

    training_kwargs = {
        "output_dir": str(output_dir),
        "num_train_epochs": config["training"].get("num_train_epochs", 1),
        "per_device_train_batch_size": config["training"].get("per_device_train_batch_size", 2),
        "per_device_eval_batch_size": config["training"].get("per_device_eval_batch_size", 2),
        "gradient_accumulation_steps": config["training"].get("gradient_accumulation_steps", 1),
        "learning_rate": config["training"].get("learning_rate", 5e-5),
        "weight_decay": config["training"].get("weight_decay", 0.0),
        "warmup_steps": config["training"].get("warmup_steps", 0),
        "logging_steps": config["training"].get("logging_steps", 10),
        "eval_steps": config["training"].get("eval_steps", 50),
        "save_steps": config["training"].get("save_steps", 50),
        "save_total_limit": config["training"].get("save_total_limit", 2),
        "predict_with_generate": config["training"].get("predict_with_generate", True),
        "generation_max_length": max_length,
        "fp16": config["training"].get("fp16", False),
        "save_strategy": "steps",
        "overwrite_output_dir": True,
        "report_to": [],
        "remove_unused_columns": False,
    }
    signature = inspect.signature(Seq2SeqTrainingArguments.__init__)
    eval_strategy = "steps" if config["training"].get("run_final_eval", False) else "no"
    if "evaluation_strategy" in signature.parameters:
        training_kwargs["evaluation_strategy"] = eval_strategy
    else:
        training_kwargs["eval_strategy"] = eval_strategy

    args = Seq2SeqTrainingArguments(**training_kwargs)

    trainer = Seq2SeqTrainer(
        model=model,
        args=args,
        train_dataset=encoded_dataset["train"],
        eval_dataset=encoded_dataset["validation"],
        data_collator=TrOCRDataCollator(processor),
        tokenizer=processor.tokenizer,
        compute_metrics=build_compute_metrics(processor),
    )

    final_dir = output_dir / "final"
    trainer.train()

    final_dir.mkdir(parents=True, exist_ok=True)
    trainer.save_model(str(final_dir))
    processor.save_pretrained(str(final_dir))

    metrics: Dict[str, Any] = {}
    if config["training"].get("run_final_eval", False):
        metrics = trainer.evaluate(encoded_dataset["test"], metric_key_prefix="test")

    metrics_path = output_dir / "final_metrics.json"
    with metrics_path.open("w", encoding="utf-8") as handle:
        json.dump({key: float(value) if isinstance(value, np.floating) else value for key, value in metrics.items()}, handle, indent=2)

    print(f"Model saved to {final_dir}")
    print(f"Metrics saved to {metrics_path}")
    print(metrics)
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description="Fine-tune TrOCR on the configured HTR dataset.")
    parser.add_argument("--config", default="config.yaml")
    args = parser.parse_args()
    train(args.config)


if __name__ == "__main__":
    main()
