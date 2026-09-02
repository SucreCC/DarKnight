"""adjust plan discount tiers: quarter 5%, half-year 10%, year 20%

Revision ID: f8b9c0d1e2f3
Revises: f7a8b9c0d1e2
Create Date: 2026-09-01 18:50:00.000000

Monthly anchor: $4.99
- quarterly:  4.99 * 3 * 0.95 = 14.22
- half-year:  4.99 * 6 * 0.90 = 26.95
- yearly:     4.99 * 12 * 0.80 = 47.90
"""
import sqlalchemy as sa
from alembic import op

revision = "f8b9c0d1e2f3"
down_revision = "f7a8b9c0d1e2"
branch_labels = None
depends_on = None

PRICES = {
    "unlimited-monthly": 4.99,
    "unlimited-quarterly": 14.22,
    "unlimited-half-year": 26.95,
    "unlimited-yearly": 47.90,
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
        "unlimited-quarterly": 12.99,
        "unlimited-half-year": 24.99,
        "unlimited-yearly": 41.99,
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
