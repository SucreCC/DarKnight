"""half-year 8% discount, yearly 22% discount

Revision ID: fd4a5b6c7d8e
Revises: fc3f4a5b6c7d
Create Date: 2026-09-01 19:40:00.000000
"""
import sqlalchemy as sa
from alembic import op

revision = "fd4a5b6c7d8e"
down_revision = "fc3f4a5b6c7d"
branch_labels = None
depends_on = None

# Monthly anchor $4.99: half-year 4.99*6*0.92=27.54; yearly 4.99*12*0.78=46.71
PRICES = {
    "unlimited-half-year": 27.54,
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
        "unlimited-half-year": 26.35,
        "unlimited-yearly": 44.91,
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
