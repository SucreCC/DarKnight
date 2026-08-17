from __future__ import annotations

import logging
import os
import subprocess
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from darknight.services.config.models import AppConfig

logger = logging.getLogger(__name__)
base_dir = Path(__file__).parent
build_dir = base_dir / "build"
statics_dir = build_dir / "statics"


def build_dashboard(vite_base_api: str) -> None:
    proc = subprocess.Popen(
        [
            "npm",
            "run",
            "build",
            "--",
            "--outDir",
            str(build_dir),
            "--assetsDir",
            "statics",
        ],
        env={**os.environ, "VITE_BASE_API": vite_base_api},
        cwd=base_dir,
        shell=os.name == "nt",
    )
    if proc.wait() != 0:
        raise RuntimeError("Dashboard build failed")


def register_dashboard(app: FastAPI, app_config: AppConfig) -> None:
    web = app_config.web
    dashboard_path = web.dashboard_path.rstrip("/") + "/"

    if not build_dir.is_dir() or not (build_dir / "index.html").exists():
        logger.info("Building dashboard (first run, may take a minute)...")
        build_dashboard(web.vite_base_api)

    app.mount(
        dashboard_path,
        StaticFiles(directory=build_dir, html=True),
        name="dashboard",
    )
    if statics_dir.is_dir():
        app.mount(
            "/statics/",
            StaticFiles(directory=statics_dir, html=True),
            name="statics",
        )


__all__ = ["register_dashboard", "build_dashboard"]
