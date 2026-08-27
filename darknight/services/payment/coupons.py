from __future__ import annotations

from datetime import date

from darknight.services.config.settings import get_app_config

# PayPal cannot capture a zero-value order, so a coupon can never take the
# charge all the way down to nothing.
MIN_CHARGE = 0.01


class CouponError(Exception):
    """Raised when a coupon code cannot be applied."""


def resolve_discount(code: str | None, amount: float) -> tuple[str | None, float]:
    """Validate a coupon against the price list and return (code, discount).

    Returns a zero discount when no code was supplied; raises CouponError when a
    code was supplied but is unknown, disabled or expired.
    """
    normalized = (code or "").strip().upper()
    if not normalized:
        return None, 0.0

    coupon = get_app_config().coupons.get(normalized)
    if not coupon or not coupon.is_valid_on(date.today()):
        raise CouponError(f"Coupon not applicable: {normalized}")

    discount = amount * coupon.percent_off / 100 + coupon.amount_off
    discount = min(round(discount, 2), round(amount - MIN_CHARGE, 2))
    if discount <= 0:
        raise CouponError(f"Coupon not applicable: {normalized}")

    return normalized, discount


__all__ = ["CouponError", "MIN_CHARGE", "resolve_discount"]
