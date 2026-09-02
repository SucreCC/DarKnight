"""tickets and ticket replies

Revision ID: d0e1f2a3b4c5
Revises: c9d0e1f2a3b4
Create Date: 2026-09-02 12:55:00.000000
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "d0e1f2a3b4c5"
down_revision = "c9d0e1f2a3b4"
branch_labels = None
depends_on = None


def _has_table(name: str) -> bool:
    return name in inspect(op.get_bind()).get_table_names()


def upgrade() -> None:
    if not _has_table("tickets"):
        op.create_table(
            "tickets",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("subject", sa.String(length=256), nullable=False),
            sa.Column(
                "priority",
                sa.Enum("low", "normal", "high", "urgent", name="ticketpriority"),
                nullable=False,
            ),
            sa.Column(
                "status",
                sa.Enum("open", "pending", "resolved", "closed", name="ticketstatus"),
                nullable=False,
            ),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.Column("last_reply_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_tickets_user_id", "tickets", ["user_id"])
        op.create_index("ix_tickets_priority", "tickets", ["priority"])
        op.create_index("ix_tickets_status", "tickets", ["status"])
        op.create_index("ix_tickets_last_reply_at", "tickets", ["last_reply_at"])

    if not _has_table("ticket_replies"):
        op.create_table(
            "ticket_replies",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("ticket_id", sa.Integer(), nullable=False),
            sa.Column(
                "author_type",
                sa.Enum("user", "admin", name="ticketauthortype"),
                nullable=False,
            ),
            sa.Column("author_id", sa.Integer(), nullable=False),
            sa.Column("content", sa.Text(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["ticket_id"], ["tickets.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_ticket_replies_ticket_id", "ticket_replies", ["ticket_id"])
        op.create_index("ix_ticket_replies_created_at", "ticket_replies", ["created_at"])


def downgrade() -> None:
    if _has_table("ticket_replies"):
        op.drop_index("ix_ticket_replies_created_at", table_name="ticket_replies")
        op.drop_index("ix_ticket_replies_ticket_id", table_name="ticket_replies")
        op.drop_table("ticket_replies")
    if _has_table("tickets"):
        op.drop_index("ix_tickets_last_reply_at", table_name="tickets")
        op.drop_index("ix_tickets_status", table_name="tickets")
        op.drop_index("ix_tickets_priority", table_name="tickets")
        op.drop_index("ix_tickets_user_id", table_name="tickets")
        op.drop_table("tickets")
