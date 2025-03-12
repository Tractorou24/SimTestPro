"""Configuration for the application."""

import json
import logging
from pathlib import Path


def _parse_config(config_path: Path) -> dict | None:
    """Parse the configuration file."""
    try:
        with config_path.open() as config_file:
            return json.load(config_file)
    except FileNotFoundError:
        logging.exception("Configuration file not found.")
    except json.JSONDecodeError:
        logging.exception("Configuration file is not valid JSON.")
    return None


class Config:
    """Configuration for the application."""

    def __init__(self, path: Path) -> None:
        """Initialize the configuration with default values."""
        # Set default values
        self.title = "Simulation Report"
        self.sim = {
            "delay": 1000,
            "timeout": 3,
        }
        self.graphs = {}

        # Load config file if it exists
        if not path.exists():
            logging.warning("Configuration file %s does not exist.", path)
        else:
            self._load_config(path)

    def _load_config(self, path: Path) -> None:
        """Load configuration from file, overriding defaults only when specified."""
        raw_config = _parse_config(path)
        if raw_config is None:
            msg = f"Invalid configuration file {path}"
            raise ValueError(msg)

        if "title" in raw_config:
            self.title = raw_config["title"]
        if "sim" in raw_config:
            for key, value in raw_config["sim"].items():
                self.sim[key] = value
        if "graphs" in raw_config:
            self.graphs = raw_config["graphs"]

    def _get_nested(self, config: dict, key: list[str], default: object) -> object:
        """Get a nested configuration value."""
        for k in key:
            if not isinstance(config, dict):
                return default
            config = config.get(k, default)
        return config

    def get(self, key: list[str], default: object = None) -> object:
        """Get a configuration value."""
        return self._get_nested(self.__dict__, key, default)
