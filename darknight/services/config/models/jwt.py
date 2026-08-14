from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class JwtConfig:
    access_token_expire_minutes: int = 1440

    @classmethod
    def from_dict(cls, raw: dict[str, Any] | None = None) -> JwtConfig:
        data = raw or {}
        return cls(
            access_token_expire_minutes=int(
                data.get("access_token_expire_minutes", cls.access_token_expire_minutes)
            )
        )


__all__ = ["JwtConfig"]
