from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ._helpers import as_tuple_str


@dataclass(frozen=True)
class WebhookConfig:
    addresses: tuple[str, ...] = ()
    secret: str | None = None

    @classmethod
    def from_dict(cls, raw: dict[str, Any] | None = None) -> WebhookConfig:
        data = raw or {}
        return cls(
            addresses=as_tuple_str(data.get("addresses", [])),
            secret=data.get("secret"),
        )


__all__ = ["WebhookConfig"]
