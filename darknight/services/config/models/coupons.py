from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any

from ._helpers import as_dict


def _parse_date(value: Any) -> date | None:
    if not value:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    try:
        return datetime.fromisoformat(str(value)).date()
    except ValueError:
        return None


@dataclass(frozen=True)
class CouponConfig:
    code: str
    percent_off: float = 0.0
    amount_off: float = 0.0
    expires_at: date | None = None
    enabled: bool = True

    def is_valid_on(self, today: date) -> bool:
        if not self.enabled:
            return False
        if self.expires_at and today > self.expires_at:
            return False
        return self.percent_off > 0 or self.amount_off > 0


@dataclass(frozen=True)
class CouponsConfig:
    items: dict[str, CouponConfig] = field(default_factory=dict)

    def get(self, code: str) -> CouponConfig | None:
        return self.items.get(code.strip().upper())

    @classmethod
    def from_dict(cls, raw: dict[str, Any] | None = None) -> CouponsConfig:
        items: dict[str, CouponConfig] = {}
        for code, item in as_dict(raw).items():
            item = as_dict(item)
            normalized = str(code).strip().upper()
            items[normalized] = CouponConfig(
                code=normalized,
                percent_off=float(item.get("percent_off", 0) or 0),
                amount_off=float(item.get("amount_off", 0) or 0),
                expires_at=_parse_date(item.get("expires_at")),
                enabled=bool(item.get("enabled", True)),
            )
        return cls(items=items)


__all__ = ["CouponConfig", "CouponsConfig"]
