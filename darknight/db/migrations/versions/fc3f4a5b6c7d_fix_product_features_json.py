"""fix product features stored as JSON strings

Revision ID: fc3f4a5b6c7d
Revises: fb2e3f4a5c6d
Create Date: 2026-09-01 19:15:00.000000
"""
import json

import sqlalchemy as sa
from alembic import op

revision = "fc3f4a5b6c7d"
down_revision = "fb2e3f4a5c6d"
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


def upgrade() -> None:
    conn = op.get_bind()
    zh_json = json.dumps(FEATURES_ZH, ensure_ascii=False)
    en_json = json.dumps(FEATURES_EN, ensure_ascii=False)
    conn.execute(
        sa.text("UPDATE products SET features_zh = :zh, features_en = :en"),
        {"zh": zh_json, "en": en_json},
    )


def downgrade() -> None:
    pass
