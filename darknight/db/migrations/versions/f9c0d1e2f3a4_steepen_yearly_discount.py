"""steepen yearly advantage vs stacking quarterly plans

Revision ID: f9c0d1e2f3a4
Revises: f8b9c0d1e2f3
Create Date: 2026-09-01 19:00:00.000000

Discount tiers (non-linear): quarter 3%, half-year 12%, year 22%
Monthly anchor $4.99:
- quarterly:  14.52  (4× = 58.08 vs year 46.71)
- half-year:  26.35
- yearly:     46.71
"""
import sqlalchemy as sa
from alembic import op

revision = "f9c0d1e2f3a4"
down_revision = "f8b9c0d1e2f3"
branch_labels = None
depends_on = None

PRICES = {
    "unlimited-monthly": 4.99,
    "unlimited-quarterly": 14.52,
    "unlimited-half-year": 26.35,
    "unlimited-yearly": 46.71,
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
        "unlimited-quarterly": 14.22,
        "unlimited-half-year": 26.95,
        "unlimited-yearly": 47.90,
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
