from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class JobsConfig:
    core_health_check_interval: int = 10
    record_node_usages_interval: int = 30
    record_user_usages_interval: int = 10
    review_users_interval: int = 10
    send_notifications_interval: int = 30

    @classmethod
    def from_dict(cls, raw: dict[str, Any] | None = None) -> JobsConfig:
        data = raw or {}
        return cls(
            core_health_check_interval=int(
                data.get("core_health_check_interval", cls.core_health_check_interval)
            ),
            record_node_usages_interval=int(
                data.get("record_node_usages_interval", cls.record_node_usages_interval)
            ),
            record_user_usages_interval=int(
                data.get("record_user_usages_interval", cls.record_user_usages_interval)
            ),
            review_users_interval=int(
                data.get("review_users_interval", cls.review_users_interval)
            ),
            send_notifications_interval=int(
                data.get("send_notifications_interval", cls.send_notifications_interval)
            ),
        )


__all__ = ["JobsConfig"]
