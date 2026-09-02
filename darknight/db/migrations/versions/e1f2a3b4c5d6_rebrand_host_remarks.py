"""rebrand default host remark templates (Marz/Marzban -> DarKnight)

Revision ID: e1f2a3b4c5d6
Revises: d0e1f2a3b4c5
Create Date: 2026-09-02 14:00:00.000000
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision = "e1f2a3b4c5d6"
down_revision = "d0e1f2a3b4c5"
branch_labels = None
depends_on = None

NEW_REMARK = "DarKnight · {USERNAME} · {PROTOCOL}"

OLD_REMARKS = (
    "🚀 Marz ({USERNAME}) [{PROTOCOL} - {TRANSPORT}]",
    "Marz ({USERNAME}) [{PROTOCOL} - {TRANSPORT}]",
    "🚀 DarKnight ({USERNAME}) [{PROTOCOL} - {TRANSPORT}]",
    "DarKnight ({USERNAME}) [{PROTOCOL} - {TRANSPORT}]",
)


def upgrade() -> None:
    if "hosts" not in inspect(op.get_bind()).get_table_names():
        return

    conn = op.get_bind()
    for old in OLD_REMARKS:
        conn.execute(
            sa.text("UPDATE hosts SET remark = :new WHERE remark = :old"),
            {"new": NEW_REMARK, "old": old},
        )


def downgrade() -> None:
    if "hosts" not in inspect(op.get_bind()).get_table_names():
        return

    conn = op.get_bind()
    conn.execute(
        sa.text("UPDATE hosts SET remark = :old WHERE remark = :new"),
        {
            "old": "🚀 DarKnight ({USERNAME}) [{PROTOCOL} - {TRANSPORT}]",
            "new": NEW_REMARK,
        },
    )
