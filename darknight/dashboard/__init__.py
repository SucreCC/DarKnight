from __future__ import annotations

import logging
import os
import subprocess
from pathlib import Path
from urllib.parse import urlsplit

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from darknight.services.config.models import AppConfig

logger = logging.getLogger(__name__)
base_dir = Path(__file__).parent
build_dir = base_dir / "dist"
statics_dir = build_dir / "assets"


def split_api_base(vite_base_api: str) -> tuple[str, str]:
    """Split the configured API base into the origin and path parts.

    The dashboard follows the yudao convention where the axios baseURL is
    composed as VITE_BASE_URL + VITE_API_URL.
    """
    parts = urlsplit(vite_base_api)
    path = parts.path.rstrip("/")
    if parts.scheme and parts.netloc:
        return f"{parts.scheme}://{parts.netloc}", path
    return "", path


def build_dashboard(vite_base_api: str) -> None:
    base_url, api_url = split_api_base(vite_base_api)
    proc = subprocess.Popen(
        ["npm", "run", "build"],
        env={
            **os.environ,
            "VITE_BASE_URL": base_url,
            "VITE_API_URL": api_url,
        },
        cwd=base_dir,
        shell=os.name == "nt",
    )
    if proc.wait() != 0:
        raise RuntimeError("Dashboard build failed")


def register_dashboard(app: FastAPI, app_config: AppConfig) -> None:
    web = app_config.web
    dashboard_path = web.dashboard_path.rstrip("/") + "/"

    logger.info("Building dashboard (may take a minute)...")
    build_dashboard(web.vite_base_api)

    if dashboard_path != "/":
        legacy_path = "/dashboard/"

        @app.get(legacy_path, include_in_schema=False)
        @app.get(legacy_path.rstrip("/"), include_in_schema=False)
        def legacy_dashboard_redirect() -> RedirectResponse:
            return RedirectResponse(url=dashboard_path, status_code=301)

    app.mount(
        dashboard_path,
        StaticFiles(directory=build_dir, html=True),
        name="dashboard",
    )
    if statics_dir.is_dir():
        app.mount(
            "/assets/",
            StaticFiles(directory=statics_dir, html=True),
            name="assets",
        )


__all__ = ["register_dashboard", "build_dashboard", "split_api_base"]
