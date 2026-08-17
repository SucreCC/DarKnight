from __future__ import annotations

import glob
import importlib
from os.path import basename, dirname, join

from ._runtime import bind
from .manager import JobManager


def register_all_jobs(manager: JobManager) -> None:
    bind(manager)

    modules = sorted(glob.glob(join(dirname(__file__), "*.py")))
    for file in modules:
        name = basename(file).replace(".py", "")
        if name in ("__init__", "manager", "_runtime"):
            continue

        module = importlib.import_module(f"{__package__}.{name}")
        register = getattr(module, "register", None)
        if register is not None:
            register(manager)


__all__ = ["JobManager", "register_all_jobs"]
