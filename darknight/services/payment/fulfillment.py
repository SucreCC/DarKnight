from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from darknight.db.models import PortalOrder, PortalOrderStatus, User, UserUsageResetLogs
from darknight.models.user import UserStatus


def try_mark_order_paid(db: Session, order: PortalOrder) -> bool:
    """Flip a pending order to paid, returning whether this caller won the race.

    Capture and webhook can both arrive for the same order, so the transition is
    a single conditional UPDATE: only the winner is allowed to fulfill.
    """
    updated = (
        db.query(PortalOrder)
        .filter(
            PortalOrder.id == order.id,
            PortalOrder.status == PortalOrderStatus.pending,
        )
        .update(
            {
                PortalOrder.status: PortalOrderStatus.paid,
                PortalOrder.paid_at: datetime.utcnow(),
            },
            synchronize_session=False,
        )
    )
    db.commit()
    db.refresh(order)
    return bool(updated)


def fulfill_portal_order(db: Session, dbuser: User, order: PortalOrder) -> User:
    """Apply a paid order to the user: full quota, reset usage, extend expiry."""
    if order.snapshot_data_limit_gb is None or order.snapshot_duration_days is None:
        raise ValueError(
            f"Order {order.id} missing fulfillment snapshot "
            f"({order.plan_id})"
        )

    if dbuser.used_traffic:
        db.add(
            UserUsageResetLogs(
                user=dbuser,
                used_traffic_at_reset=dbuser.used_traffic,
            )
        )
    dbuser.used_traffic = 0
    dbuser.node_usages.clear()

    if order.snapshot_data_limit_gb == 0:
        dbuser.data_limit = 0
    else:
        dbuser.data_limit = order.snapshot_data_limit_gb * 1024**3

    fulfill_ts = int((order.paid_at or datetime.utcnow()).timestamp())
    prior_paid_orders = (
        db.query(PortalOrder)
        .filter(
            PortalOrder.user_id == dbuser.id,
            PortalOrder.status == PortalOrderStatus.paid,
            PortalOrder.id != order.id,
        )
        .count()
    )

    if prior_paid_orders == 0:
        # First portal purchase: start from payment time, ignore any admin-set expiry.
        base_expire = fulfill_ts
    elif dbuser.expire and dbuser.expire > fulfill_ts:
        # Renewal while still active: extend from current expiry.
        base_expire = dbuser.expire
    else:
        # Renewal after expiry: start from payment time.
        base_expire = fulfill_ts

    dbuser.expire = base_expire + order.snapshot_duration_days * 86400

    if dbuser.status != UserStatus.active:
        dbuser.status = UserStatus.active
        dbuser.last_status_change = datetime.utcnow()

    db.add(dbuser)
    db.commit()
    db.refresh(dbuser)
    return dbuser


__all__ = ["fulfill_portal_order", "try_mark_order_paid"]
