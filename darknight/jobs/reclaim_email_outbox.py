"""Reclaim stuck transactional emails after restart."""

from __future__ import annotations

from sqlalchemy.exc import OperationalError, ProgrammingError

from darknight.jobs.manager import JobManager
from darknight.services.mail import mail


def reclaim_email_outbox() -> None:
    try:
        count = mail.reclaim_pending()
    except (OperationalError, ProgrammingError) as exc:
        # Table missing before migration, etc. — never block app startup.
        from darknight.jobs.manager import mgr

        mgr().logger.warning(f"Skip email outbox reclaim: {exc.orig if getattr(exc, 'orig', None) else exc}")
        return

    if count:
        from darknight.jobs.manager import mgr

        mgr().logger.info(f"Reclaimed {count} pending email outbox row(s)")


def register(manager: JobManager) -> None:
    @manager.on_startup
    def _reclaim_on_startup() -> None:
        reclaim_email_outbox()

    manager.add_job(
        reclaim_email_outbox,
        "interval",
        minutes=5,
        coalesce=True,
        max_instances=1,
        id="reclaim_email_outbox",
        replace_existing=True,
    )
