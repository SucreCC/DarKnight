"""email outbox

Revision ID: a1b2c3d4e5f6
Revises: f1a2b3c4d5e6
Create Date: 2026-08-21 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "a1b2c3d4e5f6"
down_revision = "f1a2b3c4d5e6"
branch_labels = None
depends_on = None


def _has_table(table: str) -> bool:
    bind = op.get_bind()
    return table in inspect(bind).get_table_names()


def _has_index(table: str, index: str) -> bool:
    bind = op.get_bind()
    return index in {ix["name"] for ix in inspect(bind).get_indexes(table)}


def upgrade() -> None:
    if not _has_table("email_outbox"):
        op.create_table(
            "email_outbox",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("account", sa.String(length=64), nullable=False),
            sa.Column("template", sa.String(length=128), nullable=False),
            sa.Column("to_address", sa.String(length=255), nullable=False),
            sa.Column("subject", sa.String(length=512), nullable=False),
            sa.Column("body_text", sa.Text(), nullable=False),
            sa.Column("body_html", sa.Text(), nullable=True),
            sa.Column("status", sa.String(length=32), nullable=False),
            sa.Column("attempts", sa.Integer(), nullable=False),
            sa.Column("max_attempts", sa.Integer(), nullable=False),
            sa.Column("last_error", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.Column("sent_at", sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )
    if not _has_index("email_outbox", "ix_email_outbox_to_address"):
        op.create_index(op.f("ix_email_outbox_to_address"), "email_outbox", ["to_address"], unique=False)
    if not _has_index("email_outbox", "ix_email_outbox_status"):
        op.create_index(op.f("ix_email_outbox_status"), "email_outbox", ["status"], unique=False)
    if not _has_index("email_outbox", "ix_email_outbox_status_created_at"):
        op.create_index(
            "ix_email_outbox_status_created_at",
            "email_outbox",
            ["status", "created_at"],
            unique=False,
        )


def downgrade() -> None:
    if _has_table("email_outbox"):
        if _has_index("email_outbox", "ix_email_outbox_status_created_at"):
            op.drop_index("ix_email_outbox_status_created_at", table_name="email_outbox")
        if _has_index("email_outbox", "ix_email_outbox_status"):
            op.drop_index(op.f("ix_email_outbox_status"), table_name="email_outbox")
        if _has_index("email_outbox", "ix_email_outbox_to_address"):
            op.drop_index(op.f("ix_email_outbox_to_address"), table_name="email_outbox")
        op.drop_table("email_outbox")
