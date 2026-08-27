"""portal orders

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-08-27 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "b2c3d4e5f6a7"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def _has_table(table: str) -> bool:
    bind = op.get_bind()
    return table in inspect(bind).get_table_names()


def upgrade() -> None:
    if _has_table("portal_orders"):
        return

    op.create_table(
        "portal_orders",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("plan_id", sa.String(length=32), nullable=False),
        sa.Column("cycle_id", sa.String(length=32), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("currency", sa.String(length=8), nullable=False),
        sa.Column(
            "status",
            sa.Enum("pending", "paid", "closed", "failed", name="portalorderstatus"),
            nullable=False,
        ),
        sa.Column("payment_provider", sa.String(length=32), nullable=False),
        sa.Column("paypal_order_id", sa.String(length=64), nullable=True),
        sa.Column("coupon", sa.String(length=64), nullable=True),
        sa.Column("paid_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_portal_orders_user_id"), "portal_orders", ["user_id"], unique=False)
    op.create_index(op.f("ix_portal_orders_status"), "portal_orders", ["status"], unique=False)
    op.create_index(
        op.f("ix_portal_orders_paypal_order_id"),
        "portal_orders",
        ["paypal_order_id"],
        unique=False,
    )


def downgrade() -> None:
    if not _has_table("portal_orders"):
        return
    op.drop_index(op.f("ix_portal_orders_paypal_order_id"), table_name="portal_orders")
    op.drop_index(op.f("ix_portal_orders_status"), table_name="portal_orders")
    op.drop_index(op.f("ix_portal_orders_user_id"), table_name="portal_orders")
    op.drop_table("portal_orders")
