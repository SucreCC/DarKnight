"""quarter 0% discount, yearly 25% discount

Revision ID: fa1d2e3f4b5c
Revises: f9c0d1e2f3a4
Create Date: 2026-09-01 19:05:00.000000
"""
import sqlalchemy as sa
from alembic import op

revision = "fa1d2e3f4b5c"
down_revision = "f9c0d1e2f3a4"
branch_labels = None
depends_on = None

PRICES = {
    "unlimited-monthly": 4.99,
    "unlimited-quarterly": 14.97,
    "unlimited-half-year": 26.35,
    "unlimited-yearly": 44.91,
}


def upgrade() -> None:
    conn = op.get_bind()
    for slug, price in PRICES.items():
        conn.execute(
            sa.text(
                """
                UPDATE product_cycles
                SET price = :price
                WHERE cycle_key = 'default'
                  AND product_id = (SELECT id FROM products WHERE slug = :slug)
                """
            ),
            {"slug": slug, "price": price},
        )


def downgrade() -> None:
    conn = op.get_bind()
    old = {
        "unlimited-monthly": 4.99,
        "unlimited-quarterly": 14.52,
        "unlimited-half-year": 26.35,
        "unlimited-yearly": 46.71,
    }
    for slug, price in old.items():
        conn.execute(
            sa.text(
                """
                UPDATE product_cycles
                SET price = :price
                WHERE cycle_key = 'default'
                  AND product_id = (SELECT id FROM products WHERE slug = :slug)
                """
            ),
            {"slug": slug, "price": price},
        )
