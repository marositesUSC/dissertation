from pathlib import Path
from typing import Any

import yaml


def get_project_root() -> Path:
    """
    Return the project root directory.

    This assumes this file lives at:
        src/config.py
    """
    return Path(__file__).resolve().parents[1]


def get_config_dir() -> Path:
    """
    Return the project's config directory.
    """
    return get_project_root() / "config"


def load_config(config_name: str) -> dict[str, Any]:
    """
    Load a YAML configuration file from the project's config directory.

    Parameters
    ----------
    config_name : str
        Name of the config file inside the config directory.

        Examples:
        - "paths.yml"
        - "study_area.yml"
        - "variables.yml"
        - "rq/rq1.yml"

    Returns
    -------
    dict
        Parsed YAML configuration as a Python dictionary.
    """
    config_path = get_config_dir() / config_name

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    return config if config is not None else {}