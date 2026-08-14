"""Workspace initialization helpers."""

from __future__ import annotations

import shutil
from pathlib import Path

from darknight.runtime.home import PACKAGE_ROOT, get_runtime_home
from darknight.services.path_service import get_path_service


def _seed_default_config(settings_dir: Path) -> None:
    target = settings_dir / "config.yaml"
    if target.exists():
        return

    bundled = PACKAGE_ROOT / "darknight" / "config.yaml"
    if bundled.is_file():
        shutil.copy2(bundled, target)


def init_user_directories(project_root: Path | None = None) -> Path:
    """Create ``data/user/`` layout and seed default settings when missing."""

    runtime_home = get_runtime_home(project_root)
    runtime_home.mkdir(parents=True, exist_ok=True)

    path_service = get_path_service()
    # path_service.ensure_all_directories()
    # _seed_default_config(path_service.get_settings_dir())
    return runtime_home


__all__ = [
    "init_user_directories",
]
