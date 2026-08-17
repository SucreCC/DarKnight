from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .manager import JobManager

_manager: JobManager | None = None


def bind(manager: JobManager) -> None:
    global _manager
    _manager = manager


def mgr() -> JobManager:
    if _manager is None:
        raise RuntimeError("JobManager 尚未初始化，无法执行定时任务")
    return _manager
