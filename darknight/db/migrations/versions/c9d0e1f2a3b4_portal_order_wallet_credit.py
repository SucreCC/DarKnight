"""portal order wallet credit

Revision ID: c9d0e1f2a3b4
Revises: b8c9d0e1f2a3
Create Date: 2026-09-02 11:10:00.000000
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "c9d0e1f2a3b4"
down_revision = "b8c9d0e1f2a3"
branch_labels = None
depends_on = None


def _has_column(table: str, column: str) -> bool:
    bind = op.get_bind()
    return column in {c["name"] for c in inspect(bind).get_columns(table)}


def upgrade() -> None:
    if not _has_column("portal_orders", "wallet_credit"):
        op.add_column(
            "portal_orders",
            sa.Column("wallet_credit", sa.Float(), nullable=False, server_default="0"),
        )


def downgrade() -> None:
    if _has_column("portal_orders", "wallet_credit"):
        op.drop_column("portal_orders", "wallet_credit")
