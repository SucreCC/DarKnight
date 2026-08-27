from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ._helpers import as_dict, as_tuple_str


@dataclass(frozen=True)
class LogRouteConfig:
    """把指定 logger 的记录分流到独立日志文件。"""

    filename: str = ""
    loggers: tuple[str, ...] = ()
    level: str = "INFO"
    main_log_floor: str = "WARNING"

    @classmethod
    def from_dict(cls, raw: dict[str, Any] | None = None) -> LogRouteConfig:
        data = raw or {}
        return cls(
            filename=str(data.get("filename", cls.filename)).strip(),
            loggers=as_tuple_str(data.get("loggers")),
            level=str(data.get("level", cls.level)).upper(),
            main_log_floor=str(data.get("main_log_floor", cls.main_log_floor)).upper(),
        )


@dataclass(frozen=True)
class LoggingConfig:
    namespace: str = "darknight"
    filename: str = "darknight"
    level: str = "INFO"
    console_output: bool = True
    file_output: bool = True
    log_dir: str | None = None
    backup_count: int = 30
    routes: tuple[LogRouteConfig, ...] = ()

    @classmethod
    def from_dict(cls, raw: dict[str, Any] | None = None, *, log_dir: str | None = None) -> LoggingConfig:
        data = raw or {}
        raw_routes = data.get("routes")
        routes = tuple(
            route
            for route in (
                LogRouteConfig.from_dict(as_dict(item))
                for item in (raw_routes if isinstance(raw_routes, list) else [])
            )
            if route.filename and route.loggers
        )
        return cls(
            namespace=str(data.get("namespace", cls.namespace)),
            filename=str(data.get("filename", cls.filename)),
            level=str(data.get("level", cls.level)).upper(),
            console_output=bool(data.get("console_output", cls.console_output)),
            file_output=bool(data.get("save_to_file", cls.file_output)),
            log_dir=log_dir,
            backup_count=int(data.get("backup_count", cls.backup_count)),
            routes=routes,
        )


__all__ = ["LogRouteConfig", "LoggingConfig"]
