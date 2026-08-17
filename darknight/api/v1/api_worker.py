from __future__ import annotations

import asyncio
import logging
from typing import Any

import uvicorn
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute

from darknight.api.v1.api_router import api_router
from darknight.runtime.banner import print_startup_banner
from darknight.runtime.server import build_bind_args, resolve_uvicorn_log_level
from darknight.services.config.models import AppConfig

APP_IMPORT_PATH = "darknight.api.v1.api_worker:app"


def use_route_names_as_operation_ids(app: FastAPI) -> None:
    for route in app.routes:
        if isinstance(route, APIRoute):
            route.operation_id = route.name


class APIWorker:
    """DarKnight API 服务：FastAPI 应用组装与 Uvicorn 生命周期。"""

    def __init__(self, app_config: AppConfig | None = None):
        if app_config is None:
            from darknight.services.config.settings import get_app_config

            app_config = get_app_config()
        self.app_config = app_config
        self.scheduler = BackgroundScheduler(
            {"apscheduler.job_defaults.max_instances": 20},
            timezone="UTC",
        )
        self.logger = logging.getLogger(__name__)
        self.app = self._create_app()

    def _create_app(self) -> FastAPI:
        server = self.app_config.server
        project = self.app_config.project

        app = FastAPI(
            title=project.project_name,
            description=project.description,
            version=project.version,
            docs_url=server.doc_url if server.docs else None,
            redoc_url=server.redoc_url if server.docs else None,
        )

        app.add_middleware(
            CORSMiddleware,
            allow_origins=list(server.allowed_origins),
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        app.include_router(api_router, prefix=project.api_version)

        use_route_names_as_operation_ids(app)
        self._register_lifecycle(app)
        self._register_exception_handlers(app)
        self._register_jobs(app)

        return app

    def _register_jobs(self, app: FastAPI) -> None:
        from darknight.jobs import JobManager, register_all_jobs

        self.job_manager = JobManager(
            app=app,
            scheduler=self.scheduler,
            logger=self.logger,
            config=self.app_config,
            xray=getattr(self, "xray", None),
        )
        register_all_jobs(self.job_manager)

    def _register_lifecycle(self, app: FastAPI) -> None:
        subscription_path = self.app_config.xray.subscription_path
        app_title = app.title
        scheduler = self.scheduler
        logger = self.logger

        @app.on_event("startup")
        def on_startup() -> None:
            paths = [f"{route.path}/" for route in app.routes]
            paths.append("/api/")
            if f"/{subscription_path}/" in paths:
                raise ValueError(
                    f"you can't use /{subscription_path}/ as subscription path "
                    f"it reserved for {app_title}"
                )
            scheduler.start()
            logger.info("API 服务已启动")

        @app.on_event("shutdown")
        def on_shutdown() -> None:
            scheduler.shutdown()
            logger.info("API 服务已停止")

    def _register_exception_handlers(self, app: FastAPI) -> None:
        @app.exception_handler(RequestValidationError)
        def validation_exception_handler(
            request: Request, exc: RequestValidationError
        ) -> JSONResponse:
            details: dict[str, Any] = {}
            for error in exc.errors():
                details[error["loc"][-1]] = error.get("msg")
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content=jsonable_encoder({"detail": details}),
            )

    def run(self) -> None:
        bind_args = build_bind_args(self.app_config, self.logger)
        reload = self.app_config.web.debug
        log_level = resolve_uvicorn_log_level(self.app_config)

        print_startup_banner(self.app_config, bind_args, logger=self.logger)

        try:
            if reload:
                uvicorn.run(
                    APP_IMPORT_PATH,
                    **bind_args,
                    workers=1,
                    reload=True,
                    log_level=log_level,
                )
                return

            config = uvicorn.Config(
                self.app,
                **bind_args,
                workers=1,
                reload=False,
                log_level=log_level,
            )
            asyncio.run(uvicorn.Server(config).serve())
        except FileNotFoundError:
            # Prevent error on removing unix sock
            pass


