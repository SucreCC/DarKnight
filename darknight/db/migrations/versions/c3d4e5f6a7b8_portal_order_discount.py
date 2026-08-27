"""portal order discount

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-08-27 14:40:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "c3d4e5f6a7b8"
down_revision = "b2c3d4e5f6a7"
branch_labels = None
depends_on = None


def _has_column(table: str, column: str) -> bool:
    bind = op.get_bind()
    return column in {c["name"] for c in inspect(bind).get_columns(table)}


def upgrade() -> None:
    if _has_column("portal_orders", "discount"):
        return
    op.add_column(
        "portal_orders",
        sa.Column("discount", sa.Float(), nullable=False, server_default="0"),
    )


def downgrade() -> None:
    if _has_column("portal_orders", "discount"):
        op.drop_column("portal_orders", "discount")
