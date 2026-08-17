from __future__ import annotations

import logging
from typing import Any, Callable, TypeVar

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI

from darknight.services.config.models import AppConfig

F = TypeVar("F", bound=Callable[..., Any])


class JobManager:
    """定时任务管家：统一持有调度依赖，由各 job 模块 register 登记。"""

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

    def add_job(self, *args: Any, **kwargs: Any):
        return self.scheduler.add_job(*args, **kwargs)

    def on_startup(self, func: F) -> F:
        return self.app.on_event("startup")(func)

    def on_shutdown(self, func: F) -> F:
        return self.app.on_event("shutdown")(func)


__all__ = ["JobManager"]
