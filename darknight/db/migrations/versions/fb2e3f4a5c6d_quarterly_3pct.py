"""quarterly plan 3% discount

Revision ID: fb2e3f4a5c6d
Revises: fa1d2e3f4b5c
Create Date: 2026-09-01 19:10:00.000000
"""
import sqlalchemy as sa
from alembic import op

revision = "fb2e3f4a5c6d"
down_revision = "fa1d2e3f4b5c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        sa.text(
            """
            UPDATE product_cycles
            SET price = 14.52
            WHERE cycle_key = 'default'
              AND product_id = (
                SELECT id FROM products WHERE slug = 'unlimited-quarterly'
              )
            """
        )
    )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        sa.text(
            """
            UPDATE product_cycles
            SET price = 14.97
            WHERE cycle_key = 'default'
              AND product_id = (
                SELECT id FROM products WHERE slug = 'unlimited-quarterly'
              )
            """
        )
    )
