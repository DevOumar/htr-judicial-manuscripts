from pathlib import Path
from typing import Any, Dict

import yaml


DEFAULT_CONFIG_PATH = Path("config.yaml")


def load_config(config_path: str | Path = DEFAULT_CONFIG_PATH) -> Dict[str, Any]:
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle) or {}

    return config


def ensure_directories(config: Dict[str, Any]) -> None:
    dataset = config.get("dataset", {})
    model = config.get("model", {})
    paths = config.get("paths", {})

    candidates = [
        dataset.get("cache_dir"),
        model.get("output_dir"),
        paths.get("outputs_dir"),
        paths.get("samples_dir"),
        paths.get("evaluation_dir"),
    ]

    for candidate in candidates:
        if candidate:
            Path(candidate).mkdir(parents=True, exist_ok=True)


def get_nested(config: Dict[str, Any], dotted_key: str, default: Any = None) -> Any:
    value: Any = config
    for part in dotted_key.split("."):
        if not isinstance(value, dict) or part not in value:
            return default
        value = value[part]
    return value
