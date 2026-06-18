import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable

from datasets import Dataset, DatasetDict, load_dataset

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.htr.text_normalization import normalize_transcription
from src.utils.config import ensure_directories, load_config


NORMALIZED_COLUMNS = ("image", "text", "sample_id")


def load_local_dataset() -> Dataset:
    gt_path = Path("data/sample_ground_truth/ground_truth.json")

    with gt_path.open("r", encoding="utf-8") as handle:
        rows = json.load(handle)

    normalized = []
    for index, row in enumerate(rows):
        normalized.append(
            {
                "image": str(Path("data/raw") / row["image"]),
                "text": row["text"],
                "sample_id": row.get("id", f"local_{index}"),
            }
        )

    return Dataset.from_list(normalized)


def _non_empty(values: Iterable[Any]) -> list[Any]:
    return [value for value in values if value not in (None, "", [])]


def _filter_split(dataset: Dataset, filters: Dict[str, Any]) -> Dataset:
    languages = set(_non_empty(filters.get("languages", [])))
    centuries = set(_non_empty(filters.get("centuries", [])))
    genres = set(_non_empty(filters.get("genres", [])))
    projects = set(_non_empty(filters.get("projects", [])))

    available_columns = set(dataset.column_names)

    def keep(row: Dict[str, Any]) -> bool:
        if languages and "language" in available_columns and row.get("language") not in languages:
            return False
        if centuries and "century" in available_columns and row.get("century") not in centuries:
            return False
        if genres and "genre" in available_columns and row.get("genre") not in genres:
            return False
        if projects and "project" in available_columns and row.get("project") not in projects:
            return False
        return True

    if not any((languages, centuries, genres, projects)):
        return dataset

    requested_columns = {
        "language": languages,
        "century": centuries,
        "genre": genres,
        "project": projects,
    }
    active_columns = [
        column for column, values in requested_columns.items() if values and column in available_columns
    ]
    if not active_columns:
        return dataset

    return dataset.filter(keep)


def _normalize_split(
    dataset: Dataset,
    image_column: str,
    text_column: str,
    id_column: str | None = None,
    normalization: str = "none",
) -> Dataset:
    if image_column not in dataset.column_names:
        raise ValueError(f"Image column '{image_column}' not found in dataset columns: {dataset.column_names}")
    if text_column not in dataset.column_names:
        raise ValueError(f"Text column '{text_column}' not found in dataset columns: {dataset.column_names}")

    def normalize(row: Dict[str, Any], index: int) -> Dict[str, Any]:
        sample_id = row.get(id_column) if id_column else None
        return {
            "image": row[image_column],
            "text": normalize_transcription(row[text_column], normalization),
            "sample_id": sample_id or f"sample_{index}",
        }

    return dataset.map(normalize, with_indices=True, remove_columns=dataset.column_names)


def _row_matches_filters(row: Dict[str, Any], filters: Dict[str, Any]) -> bool:
    languages = set(_non_empty(filters.get("languages", [])))
    centuries = set(_non_empty(filters.get("centuries", [])))
    genres = set(_non_empty(filters.get("genres", [])))
    projects = set(_non_empty(filters.get("projects", [])))

    if languages and "language" in row and row.get("language") not in languages:
        return False
    if centuries and "century" in row and row.get("century") not in centuries:
        return False
    if genres and "genre" in row and row.get("genre") not in genres:
        return False
    if projects and "project" in row and row.get("project") not in projects:
        return False
    return True


def _load_streaming_split(config: Dict[str, Any], split_name: str) -> Dataset:
    dataset_config = config["dataset"]
    kwargs: Dict[str, Any] = {
        "path": dataset_config["name"],
        "split": split_name,
        "streaming": True,
    }
    if dataset_config.get("config_name"):
        kwargs["name"] = dataset_config["config_name"]

    stream = load_dataset(**kwargs)
    image_column = dataset_config.get("image_column", "image")
    text_column = dataset_config.get("text_column", "text")
    id_column = dataset_config.get("id_column")
    filters = dataset_config.get("filters", {})
    normalization = dataset_config.get("text_normalization", "none")
    max_samples = dataset_config.get("max_samples", {}).get(split_name)
    max_scan = dataset_config.get("max_scan_samples_per_split", 5000)

    rows = []
    for index, row in enumerate(stream):
        if index >= max_scan:
            break
        if not _row_matches_filters(row, filters):
            continue
        rows.append(
            {
                "image": row[image_column],
                "text": normalize_transcription(row[text_column], normalization),
                "sample_id": row.get(id_column) if id_column else f"{split_name}_{index}",
            }
        )
        if max_samples and len(rows) >= max_samples:
            break

    if not rows:
        raise ValueError(
            f"No samples found for split '{split_name}' after scanning {max_scan} rows. "
            "Relax dataset.filters or increase dataset.max_scan_samples_per_split in config.yaml."
        )

    return Dataset.from_list(rows)


def _limit_split(dataset: Dataset, max_samples: int | None) -> Dataset:
    if not max_samples or max_samples <= 0 or len(dataset) <= max_samples:
        return dataset
    return dataset.select(range(max_samples))


def _ensure_three_splits(dataset: Dataset | DatasetDict, config: Dict[str, Any]) -> DatasetDict:
    split_config = config["dataset"].get("split", {})
    seed = split_config.get("seed", 42)
    validation_size = split_config.get("validation_size", 0.1)
    test_size = split_config.get("test_size", 0.1)

    if isinstance(dataset, DatasetDict):
        if {"train", "validation", "test"}.issubset(dataset.keys()):
            return dataset
        if "train" in dataset and "validation" in dataset:
            train_test = dataset["train"].train_test_split(test_size=test_size, seed=seed)
            return DatasetDict(
                train=train_test["train"],
                validation=dataset["validation"],
                test=train_test["test"],
            )
        if "train" in dataset:
            dataset = dataset["train"]
        else:
            first_split = next(iter(dataset.keys()))
            dataset = dataset[first_split]

    train_temp = dataset.train_test_split(test_size=validation_size + test_size, seed=seed)
    relative_test_size = test_size / (validation_size + test_size)
    valid_test = train_temp["test"].train_test_split(test_size=relative_test_size, seed=seed)

    return DatasetDict(
        train=train_temp["train"],
        validation=valid_test["train"],
        test=valid_test["test"],
    )


def load_hf_dataset(config: Dict[str, Any]) -> DatasetDict:
    dataset_config = config["dataset"]
    ensure_directories(config)

    if dataset_config.get("streaming", False):
        return DatasetDict(
            {
                split_name: _load_streaming_split(config, split_name)
                for split_name in ("train", "validation", "test")
            }
        )

    kwargs: Dict[str, Any] = {
        "path": dataset_config["name"],
        "cache_dir": dataset_config.get("cache_dir"),
    }
    if dataset_config.get("config_name"):
        kwargs["name"] = dataset_config["config_name"]

    raw_dataset = load_dataset(**kwargs)
    splits = _ensure_three_splits(raw_dataset, config)

    image_column = dataset_config.get("image_column", "image")
    text_column = dataset_config.get("text_column", "text")
    id_column = dataset_config.get("id_column")
    normalization = dataset_config.get("text_normalization", "none")
    filters = dataset_config.get("filters", {})
    max_samples = dataset_config.get("max_samples", {})

    processed = DatasetDict()
    for split_name, split in splits.items():
        split = _filter_split(split, filters)
        split = _normalize_split(split, image_column, text_column, id_column, normalization)
        split = _limit_split(split, max_samples.get(split_name))
        processed[split_name] = split

    return processed


def load_configured_dataset(config_path: str | Path = "config.yaml") -> DatasetDict:
    config = load_config(config_path)
    source = config.get("dataset", {}).get("source", "huggingface")

    if source == "local":
        dataset = load_local_dataset()
        splits = _ensure_three_splits(dataset, config)
        return DatasetDict({name: split for name, split in splits.items()})

    if source != "huggingface":
        raise ValueError(f"Unsupported dataset source: {source}")

    return load_hf_dataset(config)


def summarize_dataset(dataset: DatasetDict) -> None:
    for split_name, split in dataset.items():
        print(f"{split_name}: {len(split)} rows")
        print(f"  columns: {split.column_names}")
        if len(split):
            preview = split[0]["text"][:120].encode("ascii", errors="backslashreplace").decode("ascii")
            print(f"  first text: {preview}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Load and summarize the configured HTR dataset.")
    parser.add_argument("--config", default="config.yaml", help="Path to YAML config file.")
    args = parser.parse_args()

    dataset = load_configured_dataset(args.config)
    summarize_dataset(dataset)


if __name__ == "__main__":
    main()
