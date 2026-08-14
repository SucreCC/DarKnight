#!/usr/bin/env python
"""
Configuration Loader
====================

Unified configuration loading for all DeepTutor modules.
Provides YAML configuration loading, path resolution, and language parsing.
"""

import asyncio
from pathlib import Path
from typing import Any
import yaml
from darknight.runtime.home import get_runtime_home
from darknight.services.path_service import get_path_service
PROJECT_ROOT = get_runtime_home()


def _load_yaml_file(file_path: Path) -> dict[str, Any]:
    """Load a YAML file and return its contents as a dict."""
    with open(file_path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _inject_runtime_paths(config: dict[str, Any]) -> dict[str, Any]:
    """Expose canonical runtime paths without treating YAML paths as user-editable state."""
    # path_service = get_path_service()
    normalized = dict(config or {})
    return normalized


async def _load_yaml_file_async(file_path: Path) -> dict[str, Any]:
    """Async version of _load_yaml_file."""
    return await asyncio.to_thread(_load_yaml_file, file_path)


def load_config_with_main(config_file: str, top_level_package: Path | None = None) -> dict[str, Any]:
    """
    Load configuration file, automatically merge with main.yaml common configuration

    Args:
        config_file: Configuration file name (e.g., "main.yaml")
        project_root: Project root directory (if None, will try to auto-detect)

    Returns:
        Merged configuration dictionary
    """
    config_path = top_level_package / config_file
    if config_path.exists():
        return _inject_runtime_paths(_load_yaml_file(config_path))
    raise FileNotFoundError(
        f"Configuration file not found: {config_file} (expected under {top_level_package})"
    )


async def load_config_with_main_async(
    config_file: str, top_level_package: Path | None = None
) -> dict[str, Any]:
    config_path = top_level_package / config_file
    if config_path.exists():
        return _inject_runtime_paths(_load_yaml_file(config_path))
    raise FileNotFoundError(
        f"Configuration file not found: {config_file} (expected under {top_level_package})"
    )


def get_path_from_config(config: dict[str, Any], path_key: str, default: str = None) -> str:
    """
    Get path from configuration.

    Args:
        config: Configuration dictionary
        path_key: Path key name (e.g., "log_dir", "workspace")
        default: Default value

    Returns:
        Path string
    """
    injected = _inject_runtime_paths(config)
    if "paths" in injected and path_key in injected["paths"]:
        return injected["paths"][path_key]
    if path_key == "workspace":
        return injected.get("tools", {}).get("run_code", {}).get("workspace", default)
    return default




__all__ = [
    "PROJECT_ROOT",
    "load_config_with_main",
    "get_path_from_config",
]
