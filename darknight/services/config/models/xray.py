from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ._helpers import as_tuple_str


@dataclass(frozen=True)
class XrayConfig:
    json: str = "./xray_config.json"
    fallbacks_inbound_tag: str = ""
    executable_path: str = "/usr/local/bin/xray"
    assets_path: str = "/usr/local/share/xray"
    exclude_inbound_tags: tuple[str, ...] = ()
    subscription_url_prefix: str = ""
    subscription_path: str = "sub"

    @classmethod
    def from_dict(cls, raw: dict[str, Any] | None = None) -> XrayConfig:
        data = raw or {}
        return cls(
            json=str(data.get("json", cls.json)),
            fallbacks_inbound_tag=str(data.get("fallbacks_inbound_tag", cls.fallbacks_inbound_tag)),
            executable_path=str(data.get("executable_path", cls.executable_path)),
            assets_path=str(data.get("assets_path", cls.assets_path)),
            exclude_inbound_tags=as_tuple_str(data.get("exclude_inbound_tags", [])),
            subscription_url_prefix=str(
                data.get("subscription_url_prefix", cls.subscription_url_prefix)
            ),
            subscription_path=str(data.get("subscription_path", cls.subscription_path)),
        )


__all__ = ["XrayConfig"]
