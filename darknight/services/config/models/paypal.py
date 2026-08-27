from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PayPalConfig:
    client_id: str = ""
    client_secret: str = ""
    mode: str = "sandbox"  # sandbox | live
    webhook_id: str = ""
    currency: str = "USD"
    enabled: bool = False
    order_timeout_minutes: int = 30

    @property
    def api_base(self) -> str:
        if self.mode == "live":
            return "https://api-m.paypal.com"
        return "https://api-m.sandbox.paypal.com"

    @property
    def is_configured(self) -> bool:
        return self.enabled and bool(self.client_id) and bool(self.client_secret)

    @classmethod
    def from_dict(cls, raw: dict[str, Any] | None = None) -> PayPalConfig:
        data = raw or {}

        # Credentials prefer the environment so deployments don't commit secrets.
        def resolve(env_key: str, config_key: str, fallback: str) -> str:
            return str(os.getenv(env_key) or data.get(config_key, fallback))

        return cls(
            client_id=resolve("PAYPAL_CLIENT_ID", "client_id", cls.client_id),
            client_secret=resolve("PAYPAL_CLIENT_SECRET", "client_secret", cls.client_secret),
            mode=resolve("PAYPAL_MODE", "mode", cls.mode),
            webhook_id=resolve("PAYPAL_WEBHOOK_ID", "webhook_id", cls.webhook_id),
            currency=resolve("PAYPAL_CURRENCY", "currency", cls.currency).upper(),
            enabled=bool(data.get("enabled", cls.enabled)),
            order_timeout_minutes=int(
                data.get("order_timeout_minutes", cls.order_timeout_minutes)
            ),
        )


__all__ = ["PayPalConfig"]
