from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class DiscordConfig:
    webhook_url: str = ""

    @classmethod
    def from_dict(cls, raw: dict[str, Any] | None = None) -> DiscordConfig:
        data = raw or {}
        return cls(webhook_url=str(data.get("webhook_url", cls.webhook_url)))


__all__ = ["DiscordConfig"]
