"""Logging configuration loaded from runtime settings."""

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class LoggingConfig:
    namespace: str = ""
    filename: str = ""
    level: str = "INFO"
    console_output: bool = True
    file_output: bool = True
    log_dir: str | None = None
    max_bytes: int = 10 * 1024 * 1024
    backup_count: int = 5


def get_default_log_dir() -> Path:
    from darknight.services.path_service import get_path_service

    return get_path_service().get_logs_dir()


def load_logging_config() -> LoggingConfig:
    try:
        from darknight.services.config.loader import (
            load_config_with_main,
            PROJECT_ROOT
        )
        from darknight.runtime.home import get_runtime_data_root, TOP_LEVEL_PACKAGE
        config = load_config_with_main("config.yaml", TOP_LEVEL_PACKAGE)
        logging_config = config.get("logging", {}) or {}
        return LoggingConfig(
            namespace=str(logging_config.get("namespace")),
            filename=str(logging_config.get("filename")),
            level=str(logging_config.get("level", "INFO")).upper(),
            console_output=bool(logging_config.get("console_output", True)),
            file_output=bool(logging_config.get("save_to_file", True)),
            log_dir=str(get_runtime_data_root() / "logs"),
            max_bytes=int(logging_config.get("max_bytes", 10 * 1024 * 1024)),
            backup_count=int(logging_config.get("backup_count", 5)),
        )
    except Exception:
        return LoggingConfig(log_dir=str(get_default_log_dir()))


def get_global_log_level() -> str:
    return load_logging_config().level
