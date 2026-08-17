"""Startup banner for console output."""

from __future__ import annotations

import logging
import sys
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from darknight.services.config.models import AppConfig

BANNER_ART = r"""
 ██████╗  █████╗ ██████╗ ██╗  ██╗███╗   ██╗██╗ ██████╗ ██╗  ██╗████████╗
 ██╔══██╗██╔══██╗██╔══██╗██║ ██╔╝████╗  ██║██║██╔═══██╗██║ ██╔╝╚══██╔══╝
 ██║  ██║███████║██████╔╝█████╔╝ ██╔██╗ ██║██║██║   ██║█████╔╝    ██║
 ██║  ██║██╔══██║██╔══██╗██╔═██╗ ██║╚██╗██║██║██║   ██║██╔═██╗    ██║
 ██████╔╝██║  ██║██║  ██║██║  ██╗██║ ╚████║██║╚██████╔╝██║  ██╗   ██║
 ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝
"""


def _display_host(bind_args: dict[str, Any]) -> str:
    host = str(bind_args.get("host", "127.0.0.1"))
    if host == "0.0.0.0":
        return "127.0.0.1"
    return host


def _build_listen_target(app_config: AppConfig, bind_args: dict[str, Any]) -> str:
    uds = bind_args.get("uds")
    if uds:
        return f"unix://{uds}"

    host = _display_host(bind_args)
    port = bind_args.get("port", app_config.server.port)
    scheme = "https" if bind_args.get("ssl_certfile") else "http"
    return f"{scheme}://{host}:{port}"


def _join_url(base: str, path: str) -> str:
    return f"{base.rstrip('/')}/{path.lstrip('/')}"


def _build_banner_text(app_config: AppConfig, bind_args: dict[str, Any]) -> Text:
    project = app_config.project
    server = app_config.server
    web = app_config.web
    listen_target = _build_listen_target(app_config, bind_args)

    text = Text()
    text.append(BANNER_ART.strip() + "\n\n", style="bold bright_blue")

    text.append(f"{project.project_name}", style="bold white")
    text.append(f" v{project.version}\n", style="bold cyan")
    if project.description and project.description != project.project_name:
        text.append(f"{project.description}\n", style="dim")

    text.append("\n")
    text.append("Listen  ", style="bold")
    text.append(listen_target + "\n", style="green")

    if server.docs:
        text.append("Docs    ", style="bold")
        text.append(_join_url(listen_target, server.doc_url) + "\n", style="cyan")

    text.append("API     ", style="bold")
    text.append(_join_url(listen_target, project.api_version) + "\n", style="cyan")

    if web.dashboard_path:
        text.append("Panel   ", style="bold")
        text.append(_join_url(listen_target, web.dashboard_path) + "\n", style="cyan")

    text.append("\n")
    if web.debug:
        text.append("DEBUG mode enabled · hot reload on\n", style="bold yellow")
    else:
        text.append("Press CTRL+C to stop\n", style="dim")

    return text


def print_startup_banner(
    app_config: AppConfig,
    bind_args: dict[str, Any],
    *,
    logger: logging.Logger | None = None,
) -> None:
    """Print a Rich startup banner and mirror key lines to the logger."""
    project = app_config.project
    listen_target = _build_listen_target(app_config, bind_args)

    if logger is not None:
        logger.info("Starting %s v%s", project.project_name, project.version)
        logger.info("Listening on %s", listen_target)
        if app_config.web.debug:
            logger.info("Debug mode enabled with hot reload")

    if not sys.stdout.isatty():
        return

    console = Console(highlight=False)
    console.print(
        Panel(
            _build_banner_text(app_config, bind_args),
            border_style="bright_blue",
            padding=(1, 2),
        )
    )


__all__ = ["print_startup_banner"]
