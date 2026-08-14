from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class DatabaseConfig:
    url: str = "sqlite:///db.sqlite3"
    pool_size: int = 10
    max_overflow: int = 30

    @classmethod
    def from_dict(cls, raw: dict[str, Any] | None = None) -> DatabaseConfig:
        data = raw or {}
        return cls(
            url=str(data.get("url", cls.url)),
            pool_size=int(data.get("pool_size", cls.pool_size)),
            max_overflow=int(data.get("max_overflow", cls.max_overflow)),
        )


__all__ = ["DatabaseConfig"]
