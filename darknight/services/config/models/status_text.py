from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class StatusTextConfig:
    active: str = "Active"
    expired: str = "Expired"
    limited: str = "Limited"
    disabled: str = "Disabled"
    on_hold: str = "On-Hold"

    @classmethod
    def from_dict(cls, raw: dict[str, Any] | None = None) -> StatusTextConfig:
        data = raw or {}
        return cls(
            active=str(data.get("active", cls.active)),
            expired=str(data.get("expired", cls.expired)),
            limited=str(data.get("limited", cls.limited)),
            disabled=str(data.get("disabled", cls.disabled)),
            on_hold=str(data.get("on_hold", cls.on_hold)),
        )


__all__ = ["StatusTextConfig"]
