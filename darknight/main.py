import sys
from pathlib import Path

# Direct execution adds ``darknight/`` to sys.path[0], which shadows stdlib ``logging``.
_project_root = Path(__file__).resolve().parents[1]
_script_dir = Path(__file__).resolve().parent
if sys.path and Path(sys.path[0]).resolve() == _script_dir:
    sys.path.pop(0)
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

import asyncio
import logging
import os
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

import uvicorn

# Force unbuffered output
os.environ["PYTHONUNBUFFERED"] = "1"
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True, encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(line_buffering=True, encoding="utf-8", errors="replace")


def main() -> None:
    from darknight.logging import configure_logging
    from darknight.runtime.bootstrap import prepare_runtime
    from darknight.services.setup import init_user_directories

    runtime_home = prepare_runtime()
    init_user_directories(runtime_home)
    configure_logging()

    logger = logging.getLogger("main")
    logger.info("Starting Dark Night")


if __name__ == "__main__":
    main()
