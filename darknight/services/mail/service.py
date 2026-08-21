"""Transactional mail service with multi-account outbox delivery."""

from __future__ import annotations

import time
from datetime import datetime
from threading import Thread
from typing import Any

from fastapi import BackgroundTasks

from darknight import logger
from darknight.db import GetDB
from darknight.db.models import EmailOutbox
from darknight.services.config.settings import get_app_config
from darknight.services.mail.templates_loader import MailTemplateLoader
from darknight.services.mail.transport import SmtpTransport

RETRY_SLEEP_SECONDS = 2


class MailService:
    def __init__(
        self,
        templates: MailTemplateLoader | None = None,
        transport: SmtpTransport | None = None,
    ) -> None:
        self.templates = templates or MailTemplateLoader()
        self.transport = transport or SmtpTransport()

    def ensure_can_send(self, template: str, account: str | None = None) -> None:
        cfg = get_app_config().email
        cfg.get_account(account)
        self.templates.ensure_exists(template)

    def enqueue(
        self,
        *,
        template: str,
        to: str,
        context: dict[str, Any] | None = None,
        account: str | None = None,
        background_tasks: BackgroundTasks | None = None,
    ) -> int:
        outbox_id = self._create_outbox(template=template, to=to, context=context, account=account)
        self._dispatch(outbox_id, background_tasks)
        return outbox_id

    def send_now(
        self,
        *,
        template: str,
        to: str,
        context: dict[str, Any] | None = None,
        account: str | None = None,
    ) -> int:
        outbox_id = self._create_outbox(template=template, to=to, context=context, account=account)
        self.process_outbox(outbox_id)
        return outbox_id

    def _create_outbox(
        self,
        *,
        template: str,
        to: str,
        context: dict[str, Any] | None,
        account: str | None,
    ) -> int:
        cfg = get_app_config().email
        account_name = (account or cfg.default_account or "noreply").strip()
        cfg.get_account(account_name)
        rendered = self.templates.render(template, context or {})

        with GetDB() as db:
            row = EmailOutbox(
                account=account_name,
                template=template,
                to_address=to,
                subject=rendered.subject,
                body_text=rendered.body_text,
                body_html=rendered.body_html,
                status="pending",
                attempts=0,
                max_attempts=cfg.max_attempts,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            db.add(row)
            db.commit()
            db.refresh(row)
            return int(row.id)

    def _dispatch(self, outbox_id: int, background_tasks: BackgroundTasks | None) -> None:
        if background_tasks is not None:
            background_tasks.add_task(self.process_outbox, outbox_id)
            return
        Thread(target=self.process_outbox, args=(outbox_id,), daemon=True).start()

    def process_outbox(self, outbox_id: int) -> None:
        while True:
            with GetDB() as db:
                row = db.query(EmailOutbox).filter(EmailOutbox.id == outbox_id).first()
                if row is None:
                    return
                if row.status == "sent":
                    return
                if row.status == "failed" and row.attempts >= row.max_attempts:
                    return

                cfg = get_app_config().email
                row.status = "sending"
                row.updated_at = datetime.utcnow()
                db.commit()

                account_name = row.account
                to_address = row.to_address
                subject = row.subject
                body_text = row.body_text
                body_html = row.body_html
                attempts = int(row.attempts)
                max_attempts = int(row.max_attempts)

            try:
                account = cfg.get_account(account_name)
                if cfg.dev_log_only or not cfg.smtp_host:
                    logger.info(
                        f"[email/dev] id={outbox_id} account={account_name} "
                        f"to={to_address} subject={subject}"
                    )
                else:
                    self.transport.send(
                        cfg=cfg,
                        account=account,
                        to_address=to_address,
                        subject=subject,
                        body_text=body_text,
                        body_html=body_html,
                    )

                with GetDB() as db:
                    row = db.query(EmailOutbox).filter(EmailOutbox.id == outbox_id).first()
                    if row is None:
                        return
                    row.status = "sent"
                    row.sent_at = datetime.utcnow()
                    row.updated_at = datetime.utcnow()
                    row.last_error = None
                    db.commit()
                return

            except Exception as exc:
                attempts += 1
                err = str(exc)[:2000]
                logger.error(f"[email] send failed id={outbox_id} attempt={attempts}: {exc}")
                with GetDB() as db:
                    row = db.query(EmailOutbox).filter(EmailOutbox.id == outbox_id).first()
                    if row is None:
                        return
                    row.attempts = attempts
                    row.last_error = err
                    row.updated_at = datetime.utcnow()
                    if attempts >= max_attempts:
                        row.status = "failed"
                        db.commit()
                        return
                    row.status = "pending"
                    db.commit()

                time.sleep(RETRY_SLEEP_SECONDS)

    def reclaim_pending(self, limit: int = 50) -> int:
        """Re-dispatch stuck pending/sending rows after process restart."""
        with GetDB() as db:
            rows = (
                db.query(EmailOutbox)
                .filter(EmailOutbox.status.in_(("pending", "sending")))
                .filter(EmailOutbox.attempts < EmailOutbox.max_attempts)
                .order_by(EmailOutbox.created_at.asc())
                .limit(limit)
                .all()
            )
            ids = [int(r.id) for r in rows]

        for outbox_id in ids:
            self._dispatch(outbox_id, None)
        return len(ids)


mail = MailService()

__all__ = ["MailService", "mail"]
