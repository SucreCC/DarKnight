"""seed unlimited VPN plan

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-09-01 18:00:00.000000
"""
import json
from datetime import datetime

import sqlalchemy as sa
from alembic import op

revision = "e5f6a7b8c9d0"
down_revision = "d4e5f6a7b8c9"
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

CYCLES = [
    ("monthly", "包月套餐", "Monthly", 4.99, 0, 30, 0),
    ("half_year", "半年套餐", "Half-year", 24.99, 0, 180, 1),
    ("yearly", "年度套餐", "Yearly", 41.99, 0, 365, 2),
]


def upgrade() -> None:
    conn = op.get_bind()
    now = datetime.utcnow()

    conn.execute(sa.text("UPDATE products SET is_listed = 0"))
    conn.execute(sa.text("UPDATE product_cycles SET is_listed = 0"))

    row = conn.execute(sa.text("SELECT id FROM products WHERE slug = 'unlimited'")).fetchone()
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
                    display_cycle_key = 'yearly',
                    sort_order = 0,
                    is_listed = 1,
                    updated_at = :now
                WHERE id = :id
                """
            ),
            {
                "id": product_id,
                "name_zh": "无限流量 VPN",
                "name_en": "Unlimited VPN",
                "features_zh": json.dumps(FEATURES_ZH, ensure_ascii=False),
                "features_en": json.dumps(FEATURES_EN, ensure_ascii=False),
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
                    'unlimited', :name_zh, :name_en, 'period',
                    :features_zh, :features_en, 'yearly',
                    0, 1, :now, :now
                )
                """
            ),
            {
                "name_zh": "无限流量 VPN",
                "name_en": "Unlimited VPN",
                "features_zh": json.dumps(FEATURES_ZH, ensure_ascii=False),
                "features_en": json.dumps(FEATURES_EN, ensure_ascii=False),
                "now": now,
            },
        )
        product_id = conn.execute(
            sa.text("SELECT id FROM products WHERE slug = 'unlimited'")
        ).scalar()

    for cycle_key, label_zh, label_en, price, gb, days, sort_order in CYCLES:
        existing = conn.execute(
            sa.text(
                "SELECT id FROM product_cycles WHERE product_id = :pid AND cycle_key = :key"
            ),
            {"pid": product_id, "key": cycle_key},
        ).fetchone()
        if existing:
            conn.execute(
                sa.text(
                    """
                    UPDATE product_cycles SET
                        label_zh = :label_zh,
                        label_en = :label_en,
                        price = :price,
                        data_limit_gb = :gb,
                        duration_days = :days,
                        is_listed = 1,
                        sort_order = :sort_order
                    WHERE id = :id
                    """
                ),
                {
                    "id": existing[0],
                    "label_zh": label_zh,
                    "label_en": label_en,
                    "price": price,
                    "gb": gb,
                    "days": days,
                    "sort_order": sort_order,
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
                        :price, :gb, :days, 1, :sort_order
                    )
                    """
                ),
                {
                    "pid": product_id,
                    "key": cycle_key,
                    "label_zh": label_zh,
                    "label_en": label_en,
                    "price": price,
                    "gb": gb,
                    "days": days,
                    "sort_order": sort_order,
                },
            )


def downgrade() -> None:
    conn = op.get_bind()
    row = conn.execute(sa.text("SELECT id FROM products WHERE slug = 'unlimited'")).fetchone()
    if not row:
        return
    product_id = row[0]
    conn.execute(sa.text("DELETE FROM product_cycles WHERE product_id = :pid"), {"pid": product_id})
    conn.execute(sa.text("DELETE FROM products WHERE id = :id"), {"id": product_id})
