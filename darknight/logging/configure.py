"""Process-wide stdlib logging bootstrap."""

from __future__ import annotations

import logging
from pathlib import Path
import sys

from darknight.services.config.models.logging import LoggingConfig, LogRouteConfig

from .formatters import ConsoleFormatter, ContextFilter, JsonlFormatter, LoggerLevelFloorFilter
from .handlers import DailyJsonlHandler
from .loguru_bridge import install_loguru_bridge

_CONFIGURED = False
_MANAGED_ATTR = "_logging_managed"
_MANAGED_LOGGERS: list[logging.Logger] = []


def get_default_log_dir() -> Path:
    from darknight.services.path_service import get_path_service

    return get_path_service().get_logs_dir()


def load_logging_config() -> LoggingConfig:
    try:
        from darknight.services.config.settings import get_app_config

        return get_app_config().logging
    except Exception:
        return LoggingConfig(log_dir=str(get_default_log_dir()))


def get_global_log_level() -> str:
    return load_logging_config().level


def _level(value: str | int) -> int:
    if isinstance(value, int):
        return value
    return int(getattr(logging, str(value).upper(), logging.INFO))


def _managed(handler: logging.Handler) -> logging.Handler:
    setattr(handler, _MANAGED_ATTR, True)
    handler.addFilter(ContextFilter())
    return handler


def _remove_managed_handlers() -> None:
    """清掉 root 和所有分流 logger 上由本模块装的 handler。"""
    for logger in [logging.getLogger(), *_MANAGED_LOGGERS]:
        for handler in list(logger.handlers):
            if getattr(handler, _MANAGED_ATTR, False):
                logger.removeHandler(handler)
                handler.close()
    _MANAGED_LOGGERS.clear()


def _jsonl_handler(log_dir: Path, filename: str, level: int, backup_count: int) -> logging.Handler:
    handler = _managed(DailyJsonlHandler(log_dir / f"{filename}.jsonl", backup_count))
    handler.setLevel(level)
    handler.setFormatter(JsonlFormatter())
    return handler


def _route_targets(route: LogRouteConfig) -> list[str]:
    """去掉互为父子的 logger 名，否则同一条记录会被写进目标文件两次。"""
    names = sorted(set(route.loggers))
    return [
        name
        for name in names
        if not any(name.startswith(f"{other}.") for other in names if other != name)
    ]


def configure_logging(force: bool = False) -> LoggingConfig:
    """Configure stdlib logging once for the whole process."""
    global _CONFIGURED

    config = load_logging_config()
    root = logging.getLogger()
    if _CONFIGURED and not force:
        return config

    if force:
        _remove_managed_handlers()

    level = _level(config.level)
    root.setLevel(logging.DEBUG)

    # 分流走的 logger 仍然 propagate 到 root，靠这层门槛把心跳挡在主日志外，
    # 同时放行 WARNING 以上，job 抛异常时主日志和控制台依然看得到。
    routes = config.routes if config.file_output else ()
    floors = {name: _level(route.main_log_floor) for route in routes for name in route.loggers}
    floor_filter = LoggerLevelFloorFilter(floors) if floors else None

    if config.console_output:
        console = _managed(logging.StreamHandler(sys.stdout))
        console.setLevel(level)
        console.setFormatter(ConsoleFormatter())
        if floor_filter is not None:
            console.addFilter(floor_filter)
        root.addHandler(console)

    log_dir = Path(config.log_dir) if config.log_dir else get_default_log_dir()
    if config.file_output:
        log_dir.mkdir(parents=True, exist_ok=True)
        file_handler = _jsonl_handler(log_dir, config.filename, level, config.backup_count)
        if floor_filter is not None:
            file_handler.addFilter(floor_filter)
        root.addHandler(file_handler)

    for route in routes:
        route_level = _level(route.level)
        route_handler = _jsonl_handler(log_dir, route.filename, route_level, config.backup_count)
        for name in _route_targets(route):
            logger = logging.getLogger(name)
            logger.setLevel(route_level)
            logger.addHandler(route_handler)
            if logger not in _MANAGED_LOGGERS:
                _MANAGED_LOGGERS.append(logger)

    app_logger = logging.getLogger(config.namespace)
    app_logger.setLevel(logging.DEBUG)
    app_logger.propagate = True
    install_loguru_bridge(logging.DEBUG)
    _CONFIGURED = True
    return config


__all__ = [
    "LogRouteConfig",
    "LoggingConfig",
    "configure_logging",
    "get_default_log_dir",
    "get_global_log_level",
    "load_logging_config",
]
