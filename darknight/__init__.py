"""DarKnight 顶层包。"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

logger = logging.getLogger("darknight")

_scheduler: Any = None
_xray: Any = None


def __getattr__(name: str) -> Any:
    import sys

    global _scheduler, _xray
    if name == "scheduler":
        if _scheduler is None:
            from apscheduler.schedulers.background import BackgroundScheduler

            _scheduler = BackgroundScheduler()
        return _scheduler
    if name == "xray":
        if _xray is None:
            # 子模块正在加载时已在 sys.modules 中，直接返回，避免循环 __getattr__
            _xray = sys.modules.get("darknight.xray")
            if _xray is None:
                import darknight.xray as xray_module

                _xray = xray_module
        return _xray
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


if TYPE_CHECKING:
    from apscheduler.schedulers.background import BackgroundScheduler

    import darknight.xray as xray

    scheduler: BackgroundScheduler


__all__ = ["logger", "scheduler", "xray"]
