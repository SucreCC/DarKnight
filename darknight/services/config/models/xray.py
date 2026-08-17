from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from darknight.runtime.home import PACKAGE_ROOT

from ._helpers import as_tuple_str


def _resolve_path(path: str) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = PACKAGE_ROOT / candidate
    return candidate


def _resolve_executable_path(path: str) -> str:
    configured = _resolve_path(path)
    bundled = PACKAGE_ROOT / "xray" / ("xray.exe" if sys.platform == "win32" else "xray")
    for candidate in (configured, bundled):
        if candidate.is_file():
            return str(candidate)
    return str(configured)


def _resolve_assets_path(path: str) -> str:
    configured = _resolve_path(path)
    bundled = PACKAGE_ROOT / "xray"
    for candidate in (configured, bundled):
        if candidate.is_dir():
            return str(candidate)
    return str(configured)


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
            json=str(_resolve_path(data.get("json", cls.json))),
            fallbacks_inbound_tag=str(data.get("fallbacks_inbound_tag", cls.fallbacks_inbound_tag)),
            executable_path=_resolve_executable_path(str(data.get("executable_path", cls.executable_path))),
            assets_path=_resolve_assets_path(str(data.get("assets_path", cls.assets_path))),
            exclude_inbound_tags=as_tuple_str(data.get("exclude_inbound_tags", [])),
            subscription_url_prefix=str(
                data.get("subscription_url_prefix", cls.subscription_url_prefix)
            ),
            subscription_path=str(data.get("subscription_path", cls.subscription_path)),
        )


__all__ = ["XrayConfig"]
