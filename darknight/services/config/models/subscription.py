from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SubscriptionConfig:
    update_interval: str = "12"
    support_url: str = "https://t.me/"
    profile_title: str = "Subscription"

    @classmethod
    def from_dict(cls, raw: dict[str, Any] | None = None) -> SubscriptionConfig:
        data = raw or {}
        return cls(
            update_interval=str(data.get("update_interval", cls.update_interval)),
            support_url=str(data.get("support_url", cls.support_url)),
            profile_title=str(data.get("profile_title", cls.profile_title)),
        )


__all__ = ["SubscriptionConfig"]
