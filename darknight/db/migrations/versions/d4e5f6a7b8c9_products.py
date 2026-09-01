"""products catalog and order snapshots

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-09-01 12:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "d4e5f6a7b8c9"
down_revision = "c3d4e5f6a7b8"
branch_labels = None
depends_on = None


def _has_table(name: str) -> bool:
    return name in inspect(op.get_bind()).get_table_names()


def _has_column(table: str, column: str) -> bool:
    return column in {c["name"] for c in inspect(op.get_bind()).get_columns(table)}


SEED_FEATURES = {
    "100g": {
        "zh": [
            "每月 100GB 流量",
            "地区：香港、日本、新加坡、美国",
            "最高 100Mbps 峰值带宽",
            "仅限本人使用",
            "需要自己配置，记得读一下使用文档",
        ],
        "en": [
            "100GB monthly traffic",
            "Regions: HK, JP, SG, US",
            "Up to 100Mbps peak bandwidth",
            "Personal use only",
            "Self-configuration required — read the docs",
        ],
    },
    "1024g": {
        "zh": [
            "每月 1024GB 流量",
            "地区：香港、日本、新加坡、美国",
            "最高 5Gbps 峰值带宽",
            "仅限本人使用",
            "需要自己配置，记得读一下使用文档",
        ],
        "en": [
            "1024GB monthly traffic",
            "Regions: HK, JP, SG, US",
            "Up to 5Gbps peak bandwidth",
            "Personal use only",
            "Self-configuration required — read the docs",
        ],
    },
    "2048g": {
        "zh": [
            "每月 2048GB 流量",
            "地区：香港、日本、新加坡、美国",
            "最高 10Gbps 峰值带宽",
            "仅限本人使用",
            "需要自己配置，记得读一下使用文档",
        ],
        "en": [
            "2048GB monthly traffic",
            "Regions: HK, JP, SG, US",
            "Up to 10Gbps peak bandwidth",
            "Personal use only",
            "Self-configuration required — read the docs",
        ],
    },
}


def upgrade() -> None:
    if not _has_table("products"):
        op.create_table(
            "products",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("slug", sa.String(32), nullable=False),
            sa.Column("name_zh", sa.String(128), nullable=False),
            sa.Column("name_en", sa.String(128), nullable=False),
            sa.Column("category", sa.String(16), nullable=False),
            sa.Column("features_zh", sa.JSON(), nullable=False),
            sa.Column("features_en", sa.JSON(), nullable=False),
            sa.Column("display_cycle_key", sa.String(32), nullable=False),
            sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("is_listed", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.UniqueConstraint("slug"),
        )
        op.create_index("ix_products_slug", "products", ["slug"])

    if not _has_table("product_cycles"):
        op.create_table(
            "product_cycles",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
            sa.Column("cycle_key", sa.String(32), nullable=False),
            sa.Column("label_zh", sa.String(64), nullable=False),
            sa.Column("label_en", sa.String(64), nullable=False),
            sa.Column("price", sa.Float(), nullable=False),
            sa.Column("data_limit_gb", sa.Integer(), nullable=False),
            sa.Column("duration_days", sa.Integer(), nullable=False),
            sa.Column("is_listed", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
            sa.UniqueConstraint("product_id", "cycle_key", name="uq_product_cycle_key"),
        )
        op.create_index("ix_product_cycles_product_id", "product_cycles", ["product_id"])

    for col, typ in (
        ("snapshot_data_limit_gb", sa.Integer()),
        ("snapshot_duration_days", sa.Integer()),
        ("snapshot_product_name", sa.String(128)),
    ):
        if not _has_column("portal_orders", col):
            op.add_column("portal_orders", sa.Column(col, typ, nullable=True))

    # Seed only when empty
    conn = op.get_bind()
    count = conn.execute(sa.text("SELECT COUNT(*) FROM products")).scalar()
    if count:
        return

    from datetime import datetime

    now = datetime.utcnow()
    products = sa.table(
        "products",
        sa.column("id", sa.Integer),
        sa.column("slug", sa.String),
        sa.column("name_zh", sa.String),
        sa.column("name_en", sa.String),
        sa.column("category", sa.String),
        sa.column("features_zh", sa.JSON),
        sa.column("features_en", sa.JSON),
        sa.column("display_cycle_key", sa.String),
        sa.column("sort_order", sa.Integer),
        sa.column("is_listed", sa.Boolean),
        sa.column("created_at", sa.DateTime),
        sa.column("updated_at", sa.DateTime),
    )
    cycles = sa.table(
        "product_cycles",
        sa.column("product_id", sa.Integer),
        sa.column("cycle_key", sa.String),
        sa.column("label_zh", sa.String),
        sa.column("label_en", sa.String),
        sa.column("price", sa.Float),
        sa.column("data_limit_gb", sa.Integer),
        sa.column("duration_days", sa.Integer),
        sa.column("is_listed", sa.Boolean),
        sa.column("sort_order", sa.Integer),
    )

    seed_rows = [
        ("100g", "100G", "100G", "period", "yearly", 0, [
            ("yearly", "年付", "Yearly", 1.99, 100, 365, 0),
            ("two_years", "两年付", "Two years", 2.99, 100, 730, 1),
        ]),
        ("1024g", "1024G", "1024G", "traffic", "quarterly", 1, [
            ("quarterly", "季付", "Quarterly", 2.49, 1024, 90, 0),
        ]),
        ("2048g", "2048G", "2048G", "traffic", "monthly", 2, [
            ("monthly", "月付", "Monthly", 0.99, 2048, 30, 0),
        ]),
    ]

    for slug, name_zh, name_en, category, display, sort_order, cycle_defs in seed_rows:
        feat = SEED_FEATURES[slug]
        conn.execute(
            products.insert().values(
                slug=slug,
                name_zh=name_zh,
                name_en=name_en,
                category=category,
                features_zh=feat["zh"],
                features_en=feat["en"],
                display_cycle_key=display,
                sort_order=sort_order,
                is_listed=False,
                created_at=now,
                updated_at=now,
            )
        )
        pid = conn.execute(sa.text("SELECT id FROM products WHERE slug = :s"), {"s": slug}).scalar()
        for cycle_key, label_zh, label_en, price, gb, days, csort in cycle_defs:
            conn.execute(
                cycles.insert().values(
                    product_id=pid,
                    cycle_key=cycle_key,
                    label_zh=label_zh,
                    label_en=label_en,
                    price=price,
                    data_limit_gb=gb,
                    duration_days=days,
                    is_listed=False,
                    sort_order=csort,
                )
            )

    # Backfill snapshots for existing orders from known catalog
    catalog = {
        ("100g", "yearly"): (100, 365, "100G"),
        ("100g", "two_years"): (100, 730, "100G"),
        ("1024g", "quarterly"): (1024, 90, "1024G"),
        ("2048g", "monthly"): (2048, 30, "2048G"),
    }
    rows = conn.execute(sa.text("SELECT id, plan_id, cycle_id FROM portal_orders")).fetchall()
    for oid, plan_id, cycle_id in rows:
        snap = catalog.get((plan_id, cycle_id))
        if not snap:
            continue
        gb, days, pname = snap
        conn.execute(
            sa.text(
                "UPDATE portal_orders SET snapshot_data_limit_gb=:gb, "
                "snapshot_duration_days=:days, snapshot_product_name=:pname WHERE id=:id"
            ),
            {"gb": gb, "days": days, "pname": pname, "id": oid},
        )


def downgrade() -> None:
    for col in ("snapshot_product_name", "snapshot_duration_days", "snapshot_data_limit_gb"):
        if _has_column("portal_orders", col):
            op.drop_column("portal_orders", col)
    if _has_table("product_cycles"):
        op.drop_table("product_cycles")
    if _has_table("products"):
        op.drop_table("products")
