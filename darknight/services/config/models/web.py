from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class WebConfig:
    dashboard_path: str = "/"
    debug: bool = False
    vite_base_api: str = "/api/v1/"

    @classmethod
    def from_dict(
        cls,
        raw: dict[str, Any] | None = None,
        *,
        server_port: int = 33100,
        api_version: str = "/api/v1",
    ) -> WebConfig:
        data = raw or {}
        debug = bool(data.get("debug", cls.debug))
        default_api_base = f"{api_version.rstrip('/')}/"
        explicit = data.get("vite_base_api")
        if explicit is None:
            vite_base_api = default_api_base
        else:
            vite_base_api = str(explicit)
            if not vite_base_api.endswith("/"):
                vite_base_api += "/"
        if debug and explicit is None:
            vite_base_api = f"http://127.0.0.1:{server_port}{default_api_base}"
        return cls(
            dashboard_path=str(data.get("dashboard_path", cls.dashboard_path)),
            debug=debug,
            vite_base_api=vite_base_api,
        )


__all__ = ["WebConfig"]
