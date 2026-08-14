"""Load typed settings from config.yaml."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from darknight.runtime.home import TOP_LEVEL_PACKAGE

from .loader import load_config_with_main
from .models import AppConfig


def parse_app_config(raw: dict[str, Any]) -> AppConfig:
    return AppConfig.from_dict(raw)


def load_settings(config_file: str = "config.yaml") -> AppConfig:
    raw = load_config_with_main(config_file, TOP_LEVEL_PACKAGE)
    return parse_app_config(raw)


@lru_cache(maxsize=1)
def get_app_config() -> AppConfig:
    return load_settings()


__all__ = [
    "get_app_config",
    "load_settings",
    "parse_app_config",
]
