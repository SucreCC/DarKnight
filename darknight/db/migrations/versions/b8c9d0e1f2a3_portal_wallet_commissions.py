"""portal wallet, profile prefs, referral commissions

Revision ID: b8c9d0e1f2a3
Revises: a7b8c9d0e1f2
Create Date: 2026-09-02 10:30:00.000000
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "b8c9d0e1f2a3"
down_revision = "a7b8c9d0e1f2"
branch_labels = None
depends_on = None


def _has_column(table: str, column: str) -> bool:
    bind = op.get_bind()
    return column in {c["name"] for c in inspect(bind).get_columns(table)}


def _has_table(table: str) -> bool:
    bind = op.get_bind()
    return table in inspect(bind).get_table_names()


def upgrade() -> None:
    for col, col_type in (
        ("wallet_balance", sa.Float()),
        ("auto_renewal", sa.Boolean()),
        ("notify_expire_email", sa.Boolean()),
        ("notify_traffic_email", sa.Boolean()),
    ):
        if not _has_column("users", col):
            default = "0" if col == "wallet_balance" else "1" if col.startswith("notify") else "0"
            if col == "wallet_balance":
                op.add_column("users", sa.Column(col, col_type, nullable=False, server_default=default))
            else:
                op.add_column("users", sa.Column(col, col_type, nullable=False, server_default=default))

    if not _has_table("referral_commissions"):
        op.create_table(
            "referral_commissions",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("referrer_user_id", sa.Integer(), nullable=False),
            sa.Column("referred_user_id", sa.Integer(), nullable=False),
            sa.Column("order_id", sa.String(64), nullable=False),
            sa.Column("amount", sa.Float(), nullable=False),
            sa.Column("currency", sa.String(8), nullable=False, server_default="CNY"),
            sa.Column("status", sa.String(16), nullable=False, server_default="pending"),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("available_at", sa.DateTime(), nullable=False),
            sa.Column("transferred_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["referrer_user_id"], ["users.id"]),
            sa.ForeignKeyConstraint(["referred_user_id"], ["users.id"]),
            sa.ForeignKeyConstraint(["order_id"], ["portal_orders.id"]),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("order_id", name="uq_referral_commissions_order_id"),
        )
        op.create_index("ix_referral_commissions_referrer_user_id", "referral_commissions", ["referrer_user_id"])

    if not _has_table("commission_payouts"):
        op.create_table(
            "commission_payouts",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("amount", sa.Float(), nullable=False),
            sa.Column("currency", sa.String(8), nullable=False, server_default="CNY"),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_commission_payouts_user_id", "commission_payouts", ["user_id"])

    if not _has_table("wallet_redemptions"):
        op.create_table(
            "wallet_redemptions",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("coupon_code", sa.String(64), nullable=False),
            sa.Column("amount", sa.Float(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("user_id", "coupon_code", name="uq_wallet_redemptions_user_coupon"),
        )


def downgrade() -> None:
    if _has_table("wallet_redemptions"):
        op.drop_table("wallet_redemptions")
    if _has_table("commission_payouts"):
        op.drop_index("ix_commission_payouts_user_id", table_name="commission_payouts")
        op.drop_table("commission_payouts")
    if _has_table("referral_commissions"):
        op.drop_index("ix_referral_commissions_referrer_user_id", table_name="referral_commissions")
        op.drop_table("referral_commissions")

    for col in ("notify_traffic_email", "notify_expire_email", "auto_renewal", "wallet_balance"):
        if _has_column("users", col):
            op.drop_column("users", col)
