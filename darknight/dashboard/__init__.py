from __future__ import annotations

import logging
import os
import subprocess
from pathlib import Path
from urllib.parse import urlsplit

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.staticfiles import StaticFiles as StarletteStaticFiles

from darknight.services.config.models import AppConfig

logger = logging.getLogger(__name__)
base_dir = Path(__file__).parent
build_dir = base_dir / "dist"
statics_dir = build_dir / "assets"


class SPAStaticFiles(StarletteStaticFiles):
    """Serve static files and fall back to index.html for client-side routes."""

    async def get_response(self, path: str, scope):
        try:
            return await super().get_response(path, scope)
        except StarletteHTTPException as exc:
            if exc.status_code == 404:
                return await super().get_response("index.html", scope)
            raise


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


def dashboard_is_built() -> bool:
    return (build_dir / "index.html").is_file()


def build_dashboard(vite_base_api: str) -> None:
    base_url, api_url = split_api_base(vite_base_api)
    try:
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
    except FileNotFoundError as exc:
        raise RuntimeError(
            "Dashboard build requires npm, but it was not found. "
            "Prebuild with `npm run build` in darknight/dashboard, "
            "or rebuild the Docker image (which includes dist/)."
        ) from exc
    if proc.wait() != 0:
        raise RuntimeError("Dashboard build failed")


def register_dashboard(app: FastAPI, app_config: AppConfig) -> None:
    web = app_config.web
    dashboard_path = web.dashboard_path.rstrip("/") + "/"

    # Docker images ship a prebuilt dist/; skip npm there. Locally, set
    # web.debug: true to rebuild on every start, or run npm run build yourself.
    if web.debug or not dashboard_is_built():
        logger.info("Building dashboard (may take a minute)...")
        build_dashboard(web.vite_base_api)
    else:
        logger.info("Using prebuilt dashboard at %s", build_dir)

    if not dashboard_is_built():
        raise RuntimeError(
            "Dashboard dist is missing (expected index.html under "
            f"{build_dir}). Run `npm run build` in darknight/dashboard "
            "or rebuild the Docker image."
        )

    if dashboard_path != "/":
        legacy_path = "/dashboard/"

        @app.get(legacy_path, include_in_schema=False)
        @app.get(legacy_path.rstrip("/"), include_in_schema=False)
        def legacy_dashboard_redirect() -> RedirectResponse:
            return RedirectResponse(url=dashboard_path, status_code=301)

    app.mount(
        dashboard_path,
        SPAStaticFiles(directory=build_dir, html=True),
        name="dashboard",
    )
    if statics_dir.is_dir():
        app.mount(
            "/assets/",
            StarletteStaticFiles(directory=statics_dir, html=True),
            name="assets",
        )


__all__ = [
    "register_dashboard",
    "build_dashboard",
    "dashboard_is_built",
    "split_api_base",
]
