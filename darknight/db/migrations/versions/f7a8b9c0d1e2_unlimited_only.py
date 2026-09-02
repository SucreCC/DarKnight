"""remove traffic-pack products; enforce unlimited data on all plans

Revision ID: f7a8b9c0d1e2
Revises: f6a7b8c9d0e1
Create Date: 2026-09-01 18:45:00.000000
"""
import sqlalchemy as sa
from alembic import op

revision = "f7a8b9c0d1e2"
down_revision = "f6a7b8c9d0e1"
branch_labels = None
depends_on = None

LEGACY_TRAFFIC_SLUGS = ("100g", "1024g", "2048g")


def upgrade() -> None:
    conn = op.get_bind()

    for slug in LEGACY_TRAFFIC_SLUGS:
        row = conn.execute(
            sa.text("SELECT id FROM products WHERE slug = :slug"), {"slug": slug}
        ).fetchone()
        if not row:
            continue
        product_id = row[0]
        conn.execute(
            sa.text("DELETE FROM product_cycles WHERE product_id = :pid"), {"pid": product_id}
        )
        conn.execute(sa.text("DELETE FROM products WHERE id = :id"), {"id": product_id})

    conn.execute(sa.text("UPDATE product_cycles SET data_limit_gb = 0"))
    conn.execute(sa.text("UPDATE products SET category = 'period'"))


def downgrade() -> None:
    pass
