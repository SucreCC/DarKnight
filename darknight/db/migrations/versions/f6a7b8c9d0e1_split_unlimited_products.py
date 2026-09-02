"""split unlimited into four standalone products

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2026-09-01 18:30:00.000000

Quarterly price: linear interpolation between monthly (30d, $4.99)
and half-year (180d, $24.99) at 90 days -> $12.99
"""
import json
from datetime import datetime

import sqlalchemy as sa
from alembic import op

revision = "f6a7b8c9d0e1"
down_revision = "e5f6a7b8c9d0"
branch_labels = None
depends_on = None

FEATURES_ZH = [
    "无限流量",
    "地区：香港、日本、新加坡、美国",
    "高速稳定连接",
    "仅限本人使用",
    "需要自己配置，记得读一下使用文档",
]

FEATURES_EN = [
    "Unlimited traffic",
    "Regions: HK, JP, SG, US",
    "Fast and stable connection",
    "Personal use only",
    "Self-configuration required — read the docs",
]

# slug, name_zh, name_en, price, duration_days, sort_order
PRODUCTS = [
    ("unlimited-monthly", "包月套餐", "Monthly", 4.99, 30, 0),
    ("unlimited-quarterly", "季度套餐", "Quarterly", 14.52, 90, 1),
    ("unlimited-half-year", "半年套餐", "Half-year", 26.35, 180, 2),
    ("unlimited-yearly", "年度套餐", "Yearly", 44.91, 365, 3),
]

CYCLE_KEY = "default"


def _upsert_product(conn, now, slug, name_zh, name_en, price, days, sort_order):
    row = conn.execute(sa.text("SELECT id FROM products WHERE slug = :slug"), {"slug": slug}).fetchone()
    features_zh = json.dumps(FEATURES_ZH, ensure_ascii=False)
    features_en = json.dumps(FEATURES_EN, ensure_ascii=False)

    if row:
        product_id = row[0]
        conn.execute(
            sa.text(
                """
                UPDATE products SET
                    name_zh = :name_zh,
                    name_en = :name_en,
                    category = 'period',
                    features_zh = :features_zh,
                    features_en = :features_en,
                    display_cycle_key = :cycle_key,
                    sort_order = :sort_order,
                    is_listed = 1,
                    updated_at = :now
                WHERE id = :id
                """
            ),
            {
                "id": product_id,
                "name_zh": name_zh,
                "name_en": name_en,
                "features_zh": features_zh,
                "features_en": features_en,
                "cycle_key": CYCLE_KEY,
                "sort_order": sort_order,
                "now": now,
            },
        )
    else:
        conn.execute(
            sa.text(
                """
                INSERT INTO products (
                    slug, name_zh, name_en, category,
                    features_zh, features_en, display_cycle_key,
                    sort_order, is_listed, created_at, updated_at
                ) VALUES (
                    :slug, :name_zh, :name_en, 'period',
                    :features_zh, :features_en, :cycle_key,
                    :sort_order, 1, :now, :now
                )
                """
            ),
            {
                "slug": slug,
                "name_zh": name_zh,
                "name_en": name_en,
                "features_zh": features_zh,
                "features_en": features_en,
                "cycle_key": CYCLE_KEY,
                "sort_order": sort_order,
                "now": now,
            },
        )
        product_id = conn.execute(
            sa.text("SELECT id FROM products WHERE slug = :slug"), {"slug": slug}
        ).scalar()

    cycle = conn.execute(
        sa.text(
            "SELECT id FROM product_cycles WHERE product_id = :pid AND cycle_key = :key"
        ),
        {"pid": product_id, "key": CYCLE_KEY},
    ).fetchone()

    if cycle:
        conn.execute(
            sa.text(
                """
                UPDATE product_cycles SET
                    label_zh = :label_zh,
                    label_en = :label_en,
                    price = :price,
                    data_limit_gb = 0,
                    duration_days = :days,
                    is_listed = 1,
                    sort_order = 0
                WHERE id = :id
                """
            ),
            {
                "id": cycle[0],
                "label_zh": name_zh,
                "label_en": name_en,
                "price": price,
                "days": days,
            },
        )
    else:
        conn.execute(
            sa.text(
                """
                INSERT INTO product_cycles (
                    product_id, cycle_key, label_zh, label_en,
                    price, data_limit_gb, duration_days, is_listed, sort_order
                ) VALUES (
                    :pid, :key, :label_zh, :label_en,
                    :price, 0, :days, 1, 0
                )
                """
            ),
            {
                "pid": product_id,
                "key": CYCLE_KEY,
                "label_zh": name_zh,
                "label_en": name_en,
                "price": price,
                "days": days,
            },
        )


def upgrade() -> None:
    conn = op.get_bind()
    now = datetime.utcnow()

    conn.execute(sa.text("UPDATE products SET is_listed = 0"))
    conn.execute(sa.text("UPDATE product_cycles SET is_listed = 0"))

    old = conn.execute(sa.text("SELECT id FROM products WHERE slug = 'unlimited'")).fetchone()
    if old:
        conn.execute(
            sa.text("DELETE FROM product_cycles WHERE product_id = :pid"), {"pid": old[0]}
        )
        conn.execute(sa.text("DELETE FROM products WHERE id = :id"), {"id": old[0]})

    for slug, name_zh, name_en, price, days, sort_order in PRODUCTS:
        _upsert_product(conn, now, slug, name_zh, name_en, price, days, sort_order)


def downgrade() -> None:
    conn = op.get_bind()
    for slug, *_ in PRODUCTS:
        row = conn.execute(sa.text("SELECT id FROM products WHERE slug = :slug"), {"slug": slug}).fetchone()
        if not row:
            continue
        conn.execute(sa.text("DELETE FROM product_cycles WHERE product_id = :pid"), {"pid": row[0]})
        conn.execute(sa.text("DELETE FROM products WHERE id = :id"), {"id": row[0]})
