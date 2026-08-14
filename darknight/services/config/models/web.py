from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class WebConfig:
    dashboard_path: str = "/dashboard/"
    debug: bool = False
    vite_base_api: str = "/api/"

    @classmethod
    def from_dict(cls, raw: dict[str, Any] | None = None, *, server_port: int = 33100) -> WebConfig:
        data = raw or {}
        debug = bool(data.get("debug", cls.debug))
        explicit = str(data.get("vite_base_api", cls.vite_base_api))
        if debug and explicit == "/api/":
            vite_base_api = f"http://127.0.0.1:{server_port}/api/"
        else:
            vite_base_api = explicit
        return cls(
            dashboard_path=str(data.get("dashboard_path", cls.dashboard_path)),
            debug=debug,
            vite_base_api=vite_base_api,
        )


__all__ = ["WebConfig"]
