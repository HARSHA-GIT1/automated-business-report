from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).resolve().parent
CONFIG_FILE = PROJECT_ROOT / "config.yaml"


def load_config() -> dict:
    """Load project settings from config.yaml."""
    with CONFIG_FILE.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)