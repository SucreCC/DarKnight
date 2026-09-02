"""flatten products: price/duration on products, drop product_cycles

Revision ID: fe5b6c7d8e9f
Revises: fd4a5b6c7d8e
Create Date: 2026-09-02 10:00:00.000000
"""
import sqlalchemy as sa
from alembic import op

revision = "fe5b6c7d8e9f"
down_revision = "fd4a5b6c7d8e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    op.add_column("products", sa.Column("price", sa.Float(), nullable=True))
    op.add_column("products", sa.Column("duration_days", sa.Integer(), nullable=True))

    conn.execute(
        sa.text(
            """
            UPDATE products
            SET
                price = (
                    SELECT price FROM product_cycles
                    WHERE product_id = products.id
                    ORDER BY sort_order, id
                    LIMIT 1
                ),
                duration_days = (
                    SELECT duration_days FROM product_cycles
                    WHERE product_id = products.id
                    ORDER BY sort_order, id
                    LIMIT 1
                )
            """
        )
    )
    conn.execute(
        sa.text(
            """
            UPDATE products
            SET price = 4.99, duration_days = 30
            WHERE price IS NULL OR duration_days IS NULL
            """
        )
    )

    with op.batch_alter_table("products") as batch:
        batch.alter_column("price", nullable=False)
        batch.alter_column("duration_days", nullable=False)
        batch.drop_column("display_cycle_key")

    op.drop_table("product_cycles")
    conn.execute(sa.text("DELETE FROM portal_orders"))


def downgrade() -> None:
    raise NotImplementedError("flatten_products is not reversible")
