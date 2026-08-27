"""Close portal orders that were created but never paid."""

from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy.exc import OperationalError, ProgrammingError

from darknight.db import GetDB, crud
from darknight.jobs.manager import JobManager, mgr


def close_stale_orders() -> None:
    timeout_minutes = mgr().config.paypal.order_timeout_minutes
    if timeout_minutes <= 0:
        return

    cutoff = datetime.utcnow() - timedelta(minutes=timeout_minutes)
    try:
        with GetDB() as db:
            closed = crud.close_stale_portal_orders(db, cutoff)
    except (OperationalError, ProgrammingError) as exc:
        # Table missing before migration, etc. — never block the scheduler.
        mgr().logger.warning(f"Skip stale order cleanup: {getattr(exc, 'orig', None) or exc}")
        return

    if closed:
        mgr().logger.info(f"Closed {closed} unpaid portal order(s) older than {timeout_minutes}m")


def register(manager: JobManager) -> None:
    manager.add_job(
        close_stale_orders,
        "interval",
        minutes=5,
        coalesce=True,
        max_instances=1,
        id="close_stale_orders",
        replace_existing=True,
    )
