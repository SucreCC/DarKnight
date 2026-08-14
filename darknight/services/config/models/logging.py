from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class LoggingConfig:
    namespace: str = "darknight"
    filename: str = "darknight"
    level: str = "INFO"
    console_output: bool = True
    file_output: bool = True
    log_dir: str | None = None
    max_bytes: int = 10 * 1024 * 1024
    backup_count: int = 5

    @classmethod
    def from_dict(cls, raw: dict[str, Any] | None = None, *, log_dir: str | None = None) -> LoggingConfig:
        data = raw or {}
        return cls(
            namespace=str(data.get("namespace", cls.namespace)),
            filename=str(data.get("filename", cls.filename)),
            level=str(data.get("level", cls.level)).upper(),
            console_output=bool(data.get("console_output", cls.console_output)),
            file_output=bool(data.get("save_to_file", cls.file_output)),
            log_dir=log_dir,
            max_bytes=int(data.get("max_bytes", cls.max_bytes)),
            backup_count=int(data.get("backup_count", cls.backup_count)),
        )


__all__ = ["LoggingConfig"]
