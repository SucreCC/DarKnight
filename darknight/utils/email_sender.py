"""Send transactional email (verification codes, etc.)."""

from __future__ import annotations

from fastapi import BackgroundTasks

from darknight.services.mail import mail


def send_verification_email(
    to_address: str,
    code: str,
    *,
    expire_minutes: int = 5,
    background_tasks: BackgroundTasks | None = None,
) -> int:
    return mail.enqueue(
        template="verification_code",
        to=to_address,
        context={"code": code, "expire_minutes": expire_minutes},
        account="noreply",
        background_tasks=background_tasks,
    )


__all__ = ["send_verification_email"]
