"""user email auth

Revision ID: f1a2b3c4d5e6
Revises: 2b231de97dc3
Create Date: 2026-08-19 18:10:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = 'f1a2b3c4d5e6'
down_revision = '2b231de97dc3'
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
    if not _has_column("users", "email"):
        op.add_column("users", sa.Column("email", sa.String(255), nullable=True))
    if not _has_column("users", "hashed_password"):
        op.add_column("users", sa.Column("hashed_password", sa.String(128), nullable=True))
    if not _has_column("users", "email_verified_at"):
        op.add_column("users", sa.Column("email_verified_at", sa.DateTime(), nullable=True))
    if not _has_index("users", "ix_users_email"):
        op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    if not _has_table("email_verification_codes"):
        op.create_table(
            "email_verification_codes",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("email", sa.String(255), nullable=False),
            sa.Column("code", sa.String(8), nullable=False),
            sa.Column("expires_at", sa.DateTime(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
    if not _has_index("email_verification_codes", "ix_email_verification_codes_email"):
        op.create_index(
            op.f("ix_email_verification_codes_email"),
            "email_verification_codes",
            ["email"],
            unique=False,
        )


def downgrade() -> None:
    if _has_table("email_verification_codes"):
        if _has_index("email_verification_codes", "ix_email_verification_codes_email"):
            op.drop_index(
                op.f("ix_email_verification_codes_email"),
                table_name="email_verification_codes",
            )
        op.drop_table("email_verification_codes")
    if _has_index("users", "ix_users_email"):
        op.drop_index(op.f("ix_users_email"), table_name="users")
    if _has_column("users", "email_verified_at"):
        op.drop_column("users", "email_verified_at")
    if _has_column("users", "hashed_password"):
        op.drop_column("users", "hashed_password")
    if _has_column("users", "email"):
        op.drop_column("users", "email")
