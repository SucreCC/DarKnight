"""Process-level bootstrap before application modules load."""

from __future__ import annotations

import asyncio
import os
import sys


def prepare_process() -> None:
    """Configure asyncio policy and unbuffered stdio for the current process."""
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    os.environ["PYTHONUNBUFFERED"] = "1"
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(line_buffering=True, encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(line_buffering=True, encoding="utf-8", errors="replace")


__all__ = ["prepare_process"]
