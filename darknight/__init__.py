"""DarKnight 顶层包。"""

import logging
from typing import Any

logger = logging.getLogger("darknight")

_scheduler: Any = None


def __getattr__(name: str) -> Any:
    global _scheduler
    if name == "scheduler":
        if _scheduler is None:
            from apscheduler.schedulers.background import BackgroundScheduler

            _scheduler = BackgroundScheduler()
        return _scheduler
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["logger", "scheduler"]
