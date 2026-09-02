from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from darknight.db import crud
from darknight.db.models import PortalOrder, User
from darknight.services.config.settings import get_app_config

COMMISSION_RATE = 0.10
COMMISSION_CONFIRM_DAYS = 7


def _commission_currency() -> str:
    return get_app_config().paypal.currency or "USD"


def create_referral_commission_for_order(db: Session, buyer: User, order: PortalOrder) -> None:
    if not buyer.referrer_user_id or order.amount <= 0:
        return
    if crud.get_referral_commission_by_order(db, order.id):
        return

    amount = round(float(order.amount) * COMMISSION_RATE, 2)
    if amount <= 0:
        return

    crud.create_referral_commission(
        db,
        referrer_user_id=buyer.referrer_user_id,
        referred_user_id=buyer.id,
        order_id=order.id,
        amount=amount,
        currency=_commission_currency(),
        available_at=datetime.utcnow() + timedelta(days=COMMISSION_CONFIRM_DAYS),
    )
