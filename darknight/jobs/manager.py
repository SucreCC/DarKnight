from __future__ import annotations

import logging
from typing import Any, Callable, ClassVar, TypeVar

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI

from darknight.services.config.models import AppConfig

F = TypeVar("F", bound=Callable[..., Any])


class JobManager:
    """定时任务管家：统一持有调度依赖，由各 job 模块 register 登记。"""

    _current: ClassVar[JobManager | None] = None

    def __init__(
        self,
        app: FastAPI,
        scheduler: BackgroundScheduler,
        logger: logging.Logger,
        config: AppConfig,
        xray: Any = None,
    ) -> None:
        self.app = app
        self.scheduler = scheduler
        self.logger = logger
        self.config = config
        self.xray = xray

    @classmethod
    def bind(cls, manager: JobManager) -> None:
        cls._current = manager

    @classmethod
    def mgr(cls) -> JobManager:
        if cls._current is None:
            raise RuntimeError("JobManager 尚未初始化，无法执行定时任务")
        return cls._current

    def add_job(self, *args: Any, **kwargs: Any):
        return self.scheduler.add_job(*args, **kwargs)

    def on_startup(self, func: F) -> F:
        return self.app.on_event("startup")(func)

    def on_shutdown(self, func: F) -> F:
        return self.app.on_event("shutdown")(func)

    def register_all(self) -> JobManager:
        """扫描 jobs 包内各模块并调用其 register(self)，同时绑定全局 runtime。"""
        import glob
        import importlib
        from os.path import basename, dirname, join

        JobManager.bind(self)

        jobs_dir = dirname(__file__)
        package = __name__.rsplit(".", 1)[0]
        skip = {"__init__", "manager"}

        for file in sorted(glob.glob(join(jobs_dir, "*.py"))):
            name = basename(file).replace(".py", "")
            if name in skip:
                continue
            module = importlib.import_module(f"{package}.{name}")
            register = getattr(module, "register", None)
            if register is not None:
                register(self)
        return self


mgr = JobManager.mgr

__all__ = ["JobManager", "mgr"]
