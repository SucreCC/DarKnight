from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ._helpers import as_dict


@dataclass(frozen=True)
class EmailAccountConfig:
    smtp_user: str = ""
    smtp_password: str = ""
    from_address: str = ""
    from_name: str = ""


@dataclass(frozen=True)
class EmailConfig:
    smtp_host: str = ""
    smtp_port: int = 587
    use_tls: bool = True
    dev_log_only: bool = True
    default_account: str = "noreply"
    max_attempts: int = 3
    accounts: dict[str, EmailAccountConfig] = field(default_factory=dict)

    # Legacy flat fields (mapped into default account when accounts is empty)
    smtp_user: str = ""
    smtp_password: str = ""
    from_address: str = ""

    def get_account(self, name: str | None = None) -> EmailAccountConfig:
        key = (name or self.default_account or "noreply").strip()
        if key not in self.accounts:
            raise KeyError(f"Unknown email account: {key}")
        return self.accounts[key]

    @classmethod
    def from_dict(cls, raw: dict[str, Any] | None = None) -> EmailConfig:
        data = raw or {}
        accounts_raw = as_dict(data.get("accounts"))
        accounts: dict[str, EmailAccountConfig] = {}
        for name, item in accounts_raw.items():
            item = as_dict(item)
            accounts[str(name)] = EmailAccountConfig(
                smtp_user=str(item.get("smtp_user", "")),
                smtp_password=str(item.get("smtp_password", "")),
                from_address=str(item.get("from_address", "")),
                from_name=str(item.get("from_name", "")),
            )

        smtp_user = str(data.get("smtp_user", cls.smtp_user))
        smtp_password = str(data.get("smtp_password", cls.smtp_password))
        from_address = str(data.get("from_address", cls.from_address))

        if not accounts and (smtp_user or from_address):
            accounts["noreply"] = EmailAccountConfig(
                smtp_user=smtp_user,
                smtp_password=smtp_password,
                from_address=from_address or smtp_user,
                from_name="",
            )

        default_account = str(data.get("default_account", cls.default_account))
        if accounts and default_account not in accounts:
            default_account = next(iter(accounts))

        return cls(
            smtp_host=str(data.get("smtp_host", cls.smtp_host)),
            smtp_port=int(data.get("smtp_port", cls.smtp_port)),
            use_tls=bool(data.get("use_tls", cls.use_tls)),
            dev_log_only=bool(data.get("dev_log_only", cls.dev_log_only)),
            default_account=default_account,
            max_attempts=int(data.get("max_attempts", cls.max_attempts)),
            accounts=accounts,
            smtp_user=smtp_user,
            smtp_password=smtp_password,
            from_address=from_address,
        )


__all__ = ["EmailAccountConfig", "EmailConfig"]
