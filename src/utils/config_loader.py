"""
NirmaanAI Configuration Loader
Handles loading, validation, and retrieval of YAML configurations.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional
import yaml
from src.utils.logger import logger

DEFAULT_PROJECT_ROOT = Path("C:/NIRMAAN AI")

def get_project_root() -> Path:
    """Returns the primary NirmaanAI project root directory."""
    env_root = os.getenv("NIRMAANAI_ROOT")
    if env_root and Path(env_root).exists():
        return Path(env_root)
    return DEFAULT_PROJECT_ROOT

def load_yaml_config(config_path: str) -> Dict[str, Any]:
    """
    Safely loads and parses a YAML configuration file.
    
    Args:
        config_path: Absolute path or relative path to project root.
        
    Returns:
        Dictionary containing configuration parameters.
    """
    path = Path(config_path)
    if not path.is_absolute():
        path = get_project_root() / path

    if not path.exists():
        logger.error(f"Configuration file not found: {path}")
        raise FileNotFoundError(f"Configuration file not found: {path}")

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
            logger.debug(f"Loaded config from {path}")
            return data
    except Exception as e:
        logger.error(f"Error parsing YAML file {path}: {e}")
        raise

def get_base_config() -> Dict[str, Any]:
    """Retrieves system base configuration."""
    return load_yaml_config("configs/base_config.yaml")

def get_factory_defaults() -> Dict[str, Any]:
    """Retrieves default factory operational assumptions."""
    return load_yaml_config("configs/factory_defaults.yaml")
