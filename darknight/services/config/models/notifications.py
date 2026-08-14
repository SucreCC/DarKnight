from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ._helpers import as_dict, as_tuple_int


@dataclass(frozen=True)
class RecurrentNotificationConfig:
    timeout: int = 180
    count: int = 3

    @classmethod
    def from_dict(cls, raw: dict[str, Any] | None = None) -> RecurrentNotificationConfig:
        data = raw or {}
        return cls(
            timeout=int(data.get("timeout", cls.timeout)),
            count=int(data.get("count", cls.count)),
        )


@dataclass(frozen=True)
class NotificationsConfig:
    status_change: bool = True
    user_created: bool = True
    user_updated: bool = True
    user_deleted: bool = True
    user_data_used_reset: bool = True
    user_sub_revoked: bool = True
    if_data_usage_percent_reached: bool = True
    if_days_left_reached: bool = True
    login: bool = True
    reached_usage_percent: tuple[int, ...] = (80,)
    days_left: tuple[int, ...] = (3,)
    recurrent: RecurrentNotificationConfig = field(default_factory=RecurrentNotificationConfig)

    @classmethod
    def from_dict(cls, raw: dict[str, Any] | None = None) -> NotificationsConfig:
        data = raw or {}
        return cls(
            status_change=bool(data.get("status_change", cls.status_change)),
            user_created=bool(data.get("user_created", cls.user_created)),
            user_updated=bool(data.get("user_updated", cls.user_updated)),
            user_deleted=bool(data.get("user_deleted", cls.user_deleted)),
            user_data_used_reset=bool(data.get("user_data_used_reset", cls.user_data_used_reset)),
            user_sub_revoked=bool(data.get("user_sub_revoked", cls.user_sub_revoked)),
            if_data_usage_percent_reached=bool(
                data.get("if_data_usage_percent_reached", cls.if_data_usage_percent_reached)
            ),
            if_days_left_reached=bool(
                data.get("if_days_left_reached", cls.if_days_left_reached)
            ),
            login=bool(data.get("login", cls.login)),
            reached_usage_percent=as_tuple_int(
                data.get("reached_usage_percent", list(cls.reached_usage_percent))
            ),
            days_left=as_tuple_int(data.get("days_left", list(cls.days_left))),
            recurrent=RecurrentNotificationConfig.from_dict(as_dict(data.get("recurrent"))),
        )


__all__ = ["NotificationsConfig", "RecurrentNotificationConfig"]
