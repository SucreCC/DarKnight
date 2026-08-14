"""Runtime workspace bootstrap for CLI and server entry points."""

from __future__ import annotations

import os
from pathlib import Path

from darknight.runtime.home import PROJECT_HOME_ENV, get_runtime_home


def _reset_runtime_singletons() -> None:
    """Drop cached service instances so a new PROJECT_HOME takes effect."""

    try:
        from darknight.services.path_service import PathService

        PathService.reset_instance()
    except Exception:
        pass


def _refresh_loader_project_root() -> None:
    try:
        import darknight.services.config.loader as loader

        loader.PROJECT_ROOT = get_runtime_home()
    except Exception:
        pass


def prepare_runtime(home: str | Path | None = None) -> Path:
    """Resolve workspace root, pin it in the environment, and reset cached paths."""

    runtime_home = get_runtime_home(home)
    runtime_home.mkdir(parents=True, exist_ok=True)
    os.environ[PROJECT_HOME_ENV] = str(runtime_home)
    os.chdir(str(runtime_home))
    _reset_runtime_singletons()
    _refresh_loader_project_root()
    return runtime_home


__all__ = [
    "prepare_runtime",
]


if __name__ == "__main__":
    print(prepare_runtime())