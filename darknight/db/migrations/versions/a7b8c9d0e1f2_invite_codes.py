"""invite codes and user referrer

Revision ID: a7b8c9d0e1f2
Revises: fe5b6c7d8e9f
Create Date: 2026-09-02 10:20:00.000000
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "a7b8c9d0e1f2"
down_revision = "fe5b6c7d8e9f"
branch_labels = None
depends_on = None


def _has_column(table: str, column: str) -> bool:
    bind = op.get_bind()
    return column in {c["name"] for c in inspect(bind).get_columns(table)}


def _has_table(table: str) -> bool:
    bind = op.get_bind()
    return table in inspect(bind).get_table_names()


def _has_index(table: str, index: str) -> bool:
    bind = op.get_bind()
    return index in {ix["name"] for ix in inspect(bind).get_indexes(table)}


def upgrade() -> None:
    bind = op.get_bind()
    is_sqlite = bind.engine.name == "sqlite"

    if not _has_column("users", "referrer_user_id"):
        op.add_column("users", sa.Column("referrer_user_id", sa.Integer(), nullable=True))
        if not is_sqlite:
            op.create_foreign_key(
                "fk_users_referrer_user_id",
                "users",
                "users",
                ["referrer_user_id"],
                ["id"],
            )
        if not _has_index("users", "ix_users_referrer_user_id"):
            op.create_index("ix_users_referrer_user_id", "users", ["referrer_user_id"])

    if not _has_table("invite_codes"):
        op.create_table(
            "invite_codes",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("code", sa.String(16), nullable=False),
            sa.Column("owner_user_id", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("code", name="uq_invite_codes_code"),
            sa.UniqueConstraint("owner_user_id", name="uq_invite_codes_owner_user_id"),
        )
        op.create_index("ix_invite_codes_code", "invite_codes", ["code"], unique=True)
        op.create_index("ix_invite_codes_owner_user_id", "invite_codes", ["owner_user_id"], unique=True)


def downgrade() -> None:
    bind = op.get_bind()
    is_sqlite = bind.engine.name == "sqlite"

    if _has_table("invite_codes"):
        op.drop_index("ix_invite_codes_owner_user_id", table_name="invite_codes")
        op.drop_index("ix_invite_codes_code", table_name="invite_codes")
        op.drop_table("invite_codes")

    if _has_column("users", "referrer_user_id"):
        if _has_index("users", "ix_users_referrer_user_id"):
            op.drop_index("ix_users_referrer_user_id", table_name="users")
        if not is_sqlite:
            op.drop_constraint("fk_users_referrer_user_id", "users", type_="foreignkey")
        op.drop_column("users", "referrer_user_id")
