"""SMTP transport for transactional mail."""

from __future__ import annotations

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

from darknight.services.config.models.email import EmailAccountConfig, EmailConfig


class SmtpTransport:
    def send(
        self,
        *,
        cfg: EmailConfig,
        account: EmailAccountConfig,
        to_address: str,
        subject: str,
        body_text: str,
        body_html: str | None = None,
    ) -> None:
        from_addr = account.from_address or account.smtp_user
        from_header = formataddr((account.from_name, from_addr)) if account.from_name else from_addr

        if body_html:
            msg: MIMEMultipart | MIMEText = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = from_header
            msg["To"] = to_address
            msg.attach(MIMEText(body_text, "plain", "utf-8"))
            msg.attach(MIMEText(body_html, "html", "utf-8"))
        else:
            msg = MIMEText(body_text, "plain", "utf-8")
            msg["Subject"] = subject
            msg["From"] = from_header
            msg["To"] = to_address

        with smtplib.SMTP(cfg.smtp_host, cfg.smtp_port, timeout=30) as server:
            if cfg.use_tls:
                server.starttls()
            if account.smtp_user:
                server.login(account.smtp_user, account.smtp_password)
            server.sendmail(from_addr, [to_address], msg.as_string())


__all__ = ["SmtpTransport"]
