from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ._helpers import as_tuple_int


@dataclass(frozen=True)
class TelegramConfig:
    api_token: str = ""
    admin_id: tuple[int, ...] = ()
    proxy_url: str = ""
    logger_channel_id: int = 0
    default_vless_flow: str = ""

    @classmethod
    def from_dict(cls, raw: dict[str, Any] | None = None) -> TelegramConfig:
        data = raw or {}
        return cls(
            api_token=str(data.get("api_token", cls.api_token)),
            admin_id=as_tuple_int(data.get("admin_id", [])),
            proxy_url=str(data.get("proxy_url", cls.proxy_url)),
            logger_channel_id=int(data.get("logger_channel_id", cls.logger_channel_id)),
            default_vless_flow=str(data.get("default_vless_flow", cls.default_vless_flow)),
        )


__all__ = ["TelegramConfig"]
