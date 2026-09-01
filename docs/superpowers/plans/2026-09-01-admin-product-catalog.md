# Admin Product Catalog Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 用 DB 商品目录（`Product` + `ProductCycle`）替换硬编码套餐，提供管理端 CRUD（上下架/增删改），并让门户购买与履约全部走数据库与订单快照。

**Architecture:** 两表商品模型；Admin CRUD 对齐 Node 模式；公开 `GET /plans` 只返回双上架商品并附带中英文案；下单写入履约快照；`fulfill_portal_order` 只读快照。种子导入现有 3 套餐，默认全部下架。

**Tech Stack:** FastAPI、SQLAlchemy、Alembic、Pydantic、Vue 3、TanStack Query、现有 shadcn/ui admin 组件

**Spec:** `docs/superpowers/specs/2026-09-01-admin-product-catalog-design.md`

## Global Constraints

- 仓库根：`e:\kai\DarKnight`；前端目录：`darknight/dashboard`。
- 写操作 Admin 使用 `Admin.check_sudo_admin`；读列表用 `Admin.get_current`（对齐 Node）。
- 门户可见：`product.is_listed` 且至少一周期 `is_listed`；下单要求双上架。
- 硬删：存在引用该 `plan_id`(=slug) 或 `(plan_id, cycle_id)` 的 `pending` 订单 → HTTP 409。
- 删除商品级联删除周期；删除 `display_cycle_key` 对应周期前须先改商品展示周期，否则 400。
- 校验：`price > 0`，`data_limit_gb > 0`，`duration_days > 0`；`slug` 与 `(product_id, cycle_key)` 唯一。
- 订单字段名保持 `plan_id` / `cycle_id`（语义 = slug / cycle_key）。
- 文案仅 zh/en；其他语言回退 en。
- 本仓库无 pytest：每个 Task 用明确手工/命令验收，不新建测试框架。
- Alembic `down_revision` = `c3d4e5f6a7b8`（当前 head）。
- 提交信息风格：`feat(payment): ...` / `feat(dashboard): ...`。

## File Map

| 文件 | 职责 |
|------|------|
| `darknight/db/models.py` | `Product`、`ProductCycle` ORM；`PortalOrder` 快照列 |
| `darknight/db/migrations/versions/d4e5f6a7b8c9_products.py` | 建表、快照列、种子（默认下架） |
| `darknight/models/product.py` | Admin/共享 Pydantic schemas |
| `darknight/models/order.py` | 扩展公开 `Plan*` 响应（中英 name/features/labels） |
| `darknight/db/crud.py` | 商品/周期 CRUD；订单创建写入快照；pending 引用检查 |
| `darknight/api/v1/routers/product.py` | Admin 商品 API |
| `darknight/api/v1/routers/__init__.py`、`api_router.py` | 注册 router |
| `darknight/api/v1/routers/order.py` | `/plans`、优惠券、下单改读 DB |
| `darknight/services/payment/fulfillment.py` | 履约读快照 |
| `darknight/services/payment/plans.py` | 退役硬编码；可保留薄查询或删除并改 import |
| `darknight/dashboard/src/api/product/` | Admin 前端 API |
| `darknight/dashboard/src/views/admin/Product/` | 管理页 |
| `darknight/dashboard/src/router/admin.ts` | `/admin/products` |
| `darknight/dashboard/src/layout/components/Menu/index.vue` | 侧栏图标 |
| `darknight/dashboard/src/locales/{zh,en,ru,fa}.json` | 管理端文案键 |
| `darknight/dashboard/src/api/portal/orders.ts` | 扩展 Plan 类型 |
| `darknight/dashboard/src/views/portal/Buy/plans.ts` | 工具函数；移除硬编码 `PLAN_META` |
| `darknight/dashboard/src/views/portal/Buy/usePlanCatalog.ts` | 完全消费 `/plans` |
| `darknight/dashboard/src/views/portal/Buy/index.vue`、`Configure.vue` | 按语言显示 name/features/labels |

---

### Task 1: ORM 模型

**Files:**
- Modify: `darknight/db/models.py`

**Interfaces:**
- Produces:
  - `class Product` → table `products`
  - `class ProductCycle` → table `product_cycles`
  - `PortalOrder` 新增可空：`snapshot_data_limit_gb: int`、`snapshot_duration_days: int`、`snapshot_product_name: str`

- [ ] **Step 1: 在 `PortalOrder` 附近增加模型**

在 `darknight/db/models.py` 中（`PortalOrder` 定义之前或之后均可，保持风格一致）加入：

```python
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    slug = Column(String(32), nullable=False, unique=True, index=True)
    name_zh = Column(String(128), nullable=False)
    name_en = Column(String(128), nullable=False)
    category = Column(String(16), nullable=False)  # period | traffic
    features_zh = Column(JSON, nullable=False, default=list)
    features_en = Column(JSON, nullable=False, default=list)
    display_cycle_key = Column(String(32), nullable=False)
    sort_order = Column(Integer, nullable=False, default=0)
    is_listed = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    cycles = relationship(
        "ProductCycle",
        back_populates="product",
        cascade="all, delete-orphan",
        order_by="ProductCycle.sort_order",
    )


class ProductCycle(Base):
    __tablename__ = "product_cycles"
    __table_args__ = (
        UniqueConstraint("product_id", "cycle_key", name="uq_product_cycle_key"),
    )

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    cycle_key = Column(String(32), nullable=False)
    label_zh = Column(String(64), nullable=False)
    label_en = Column(String(64), nullable=False)
    price = Column(Float, nullable=False)
    data_limit_gb = Column(Integer, nullable=False)
    duration_days = Column(Integer, nullable=False)
    is_listed = Column(Boolean, nullable=False, default=False)
    sort_order = Column(Integer, nullable=False, default=0)

    product = relationship("Product", back_populates="cycles")
```

确保文件顶部已 import：`Boolean`、`JSON`、`UniqueConstraint`（若缺失则补上）。

- [ ] **Step 2: 扩展 `PortalOrder`**

在现有列后增加：

```python
snapshot_data_limit_gb = Column(Integer, nullable=True)
snapshot_duration_days = Column(Integer, nullable=True)
snapshot_product_name = Column(String(128), nullable=True)
```

- [ ] **Step 3: Commit**

```bash
git add darknight/db/models.py
git commit -m "feat(payment): add Product ORM and order snapshot columns"
```

---

### Task 2: Alembic 迁移 + 种子

**Files:**
- Create: `darknight/db/migrations/versions/d4e5f6a7b8c9_products.py`

**Interfaces:**
- Consumes: Task 1 表结构
- Produces: revision `d4e5f6a7b8c9`，`down_revision = "c3d4e5f6a7b8"`；种子 3 商品全部 `is_listed=false`

- [ ] **Step 1: 写迁移文件**

创建 `darknight/db/migrations/versions/d4e5f6a7b8c9_products.py`：

```python
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

    import json
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
```

（若项目 JSON 列在 SQLite 下对 list 插入有问题，改为 `json.dumps(feat["zh"])` 并确认 ORM 侧可反序列化；按实际 DB 方言调整。）

- [ ] **Step 2: 跑迁移**

```bash
# 使用项目惯用 alembic 入口（若有 make/脚本则用脚本；否则）
cd e:\kai\DarKnight
alembic -c <项目 alembic.ini 路径> upgrade head
```

Expected: 无报错；`products` 有 3 行且 `is_listed=0`。

- [ ] **Step 3: Commit**

```bash
git add darknight/db/migrations/versions/d4e5f6a7b8c9_products.py
git commit -m "feat(payment): migrate products catalog with unlisted seed"
```

---

### Task 3: Pydantic schemas

**Files:**
- Create: `darknight/models/product.py`
- Modify: `darknight/models/order.py`

**Interfaces:**
- Produces（product.py）:
  - `ProductCycleCreate` / `ProductCycleModify` / `ProductCycleResponse`
  - `ProductCreate` / `ProductModify` / `ProductResponse`（含 `cycles: list[ProductCycleResponse]`）
- Produces（order.py 扩展公开目录）:
  - `PlanCycleResponse` 增加 `label_zh`、`label_en`
  - `PlanResponse` 增加 `name_zh`、`name_en`、`category`、`features_zh`、`features_en`、`display_cycle_id`、`sort_order`

- [ ] **Step 1: 创建 `darknight/models/product.py`**

```python
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


ProductCategory = Literal["period", "traffic"]


class ProductCycleCreate(BaseModel):
    cycle_key: str = Field(min_length=1, max_length=32)
    label_zh: str = Field(min_length=1, max_length=64)
    label_en: str = Field(min_length=1, max_length=64)
    price: float
    data_limit_gb: int
    duration_days: int
    is_listed: bool = False
    sort_order: int = 0

    @field_validator("price")
    @classmethod
    def price_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("price must be > 0")
        return v

    @field_validator("data_limit_gb", "duration_days")
    @classmethod
    def positive_int(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("must be > 0")
        return v


class ProductCycleModify(BaseModel):
    cycle_key: Optional[str] = Field(default=None, min_length=1, max_length=32)
    label_zh: Optional[str] = Field(default=None, min_length=1, max_length=64)
    label_en: Optional[str] = Field(default=None, min_length=1, max_length=64)
    price: Optional[float] = None
    data_limit_gb: Optional[int] = None
    duration_days: Optional[int] = None
    is_listed: Optional[bool] = None
    sort_order: Optional[int] = None

    @field_validator("price")
    @classmethod
    def price_positive(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v <= 0:
            raise ValueError("price must be > 0")
        return v

    @field_validator("data_limit_gb", "duration_days")
    @classmethod
    def positive_int(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v <= 0:
            raise ValueError("must be > 0")
        return v


class ProductCycleResponse(BaseModel):
    id: int
    cycle_key: str
    label_zh: str
    label_en: str
    price: float
    data_limit_gb: int
    duration_days: int
    is_listed: bool
    sort_order: int

    model_config = {"from_attributes": True}


class ProductCreate(BaseModel):
    slug: str = Field(min_length=1, max_length=32)
    name_zh: str = Field(min_length=1, max_length=128)
    name_en: str = Field(min_length=1, max_length=128)
    category: ProductCategory
    features_zh: list[str] = Field(default_factory=list)
    features_en: list[str] = Field(default_factory=list)
    display_cycle_key: str = Field(min_length=1, max_length=32)
    sort_order: int = 0
    is_listed: bool = False
    cycles: list[ProductCycleCreate] = Field(default_factory=list)


class ProductModify(BaseModel):
    slug: Optional[str] = Field(default=None, min_length=1, max_length=32)
    name_zh: Optional[str] = Field(default=None, min_length=1, max_length=128)
    name_en: Optional[str] = Field(default=None, min_length=1, max_length=128)
    category: Optional[ProductCategory] = None
    features_zh: Optional[list[str]] = None
    features_en: Optional[list[str]] = None
    display_cycle_key: Optional[str] = Field(default=None, min_length=1, max_length=32)
    sort_order: Optional[int] = None
    is_listed: Optional[bool] = None


class ProductResponse(BaseModel):
    id: int
    slug: str
    name_zh: str
    name_en: str
    category: str
    features_zh: list[str]
    features_en: list[str]
    display_cycle_key: str
    sort_order: int
    is_listed: bool
    created_at: datetime
    updated_at: datetime
    cycles: list[ProductCycleResponse] = Field(default_factory=list)

    model_config = {"from_attributes": True}
```

- [ ] **Step 2: 扩展 `darknight/models/order.py` 的 Plan 响应**

```python
class PlanCycleResponse(BaseModel):
    cycle_id: str
    price: float
    data_limit_gb: int
    duration_days: int
    label_zh: str = ""
    label_en: str = ""


class PlanResponse(BaseModel):
    plan_id: str
    name_zh: str = ""
    name_en: str = ""
    category: str = "period"
    features_zh: list[str] = Field(default_factory=list)
    features_en: list[str] = Field(default_factory=list)
    display_cycle_id: str = ""
    sort_order: int = 0
    cycles: list[PlanCycleResponse]
```

（保留默认值，避免旧调用方瞬时破坏；新 `/plans` 会填满。）

- [ ] **Step 3: Commit**

```bash
git add darknight/models/product.py darknight/models/order.py
git commit -m "feat(payment): add product and extended plan schemas"
```

---

### Task 4: CRUD

**Files:**
- Modify: `darknight/db/crud.py`

**Interfaces:**
- Produces 函数（签名固定，供 router 使用）:
  - `list_products(db) -> list[Product]`
  - `get_product(db, product_id: int) -> Product | None`
  - `get_product_by_slug(db, slug: str) -> Product | None`
  - `create_product(db, payload: ProductCreate) -> Product`
  - `update_product(db, product: Product, payload: ProductModify) -> Product`
  - `remove_product(db, product: Product) -> None`
  - `get_product_cycle(db, cycle_id: int) -> ProductCycle | None`
  - `add_product_cycle(db, product: Product, payload: ProductCycleCreate) -> ProductCycle`
  - `update_product_cycle(db, cycle: ProductCycle, payload: ProductCycleModify) -> ProductCycle`
  - `remove_product_cycle(db, cycle: ProductCycle) -> None`
  - `list_listed_products(db) -> list[Product]`（仅门户：商品上架且过滤出上架周期）
  - `get_listed_cycle(db, slug: str, cycle_key: str) -> tuple[Product, ProductCycle] | None`
  - `has_pending_orders_for_product(db, slug: str) -> bool`
  - `has_pending_orders_for_cycle(db, slug: str, cycle_key: str) -> bool`
  - 扩展 `create_portal_order(..., snapshot_data_limit_gb, snapshot_duration_days, snapshot_product_name)`

- [ ] **Step 1: 在 `crud.py` 增加上述函数**

实现要点：

```python
def create_product(db: Session, payload: ProductCreate) -> Product:
    keys = {c.cycle_key for c in payload.cycles}
    if payload.cycles and payload.display_cycle_key not in keys:
        raise ValueError("display_cycle_key must match a cycle")
    product = Product(
        slug=payload.slug,
        name_zh=payload.name_zh,
        name_en=payload.name_en,
        category=payload.category,
        features_zh=payload.features_zh,
        features_en=payload.features_en,
        display_cycle_key=payload.display_cycle_key,
        sort_order=payload.sort_order,
        is_listed=payload.is_listed,
    )
    for c in payload.cycles:
        product.cycles.append(ProductCycle(**c.model_dump()))
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def list_listed_products(db: Session) -> list[Product]:
    products = (
        db.query(Product)
        .filter(Product.is_listed.is_(True))
        .order_by(Product.sort_order.asc(), Product.id.asc())
        .all()
    )
    result = []
    for p in products:
        listed = [c for c in p.cycles if c.is_listed]
        if not listed:
            continue
        # 调用方只应暴露 listed cycles；可在 router 层过滤
        result.append(p)
    return result


def get_listed_cycle(db: Session, slug: str, cycle_key: str):
    product = get_product_by_slug(db, slug)
    if not product or not product.is_listed:
        return None
    cycle = next((c for c in product.cycles if c.cycle_key == cycle_key and c.is_listed), None)
    if not cycle:
        return None
    return product, cycle


def has_pending_orders_for_product(db: Session, slug: str) -> bool:
    return (
        db.query(PortalOrder)
        .filter(
            PortalOrder.plan_id == slug,
            PortalOrder.status == PortalOrderStatus.pending,
        )
        .first()
        is not None
    )


def has_pending_orders_for_cycle(db: Session, slug: str, cycle_key: str) -> bool:
    return (
        db.query(PortalOrder)
        .filter(
            PortalOrder.plan_id == slug,
            PortalOrder.cycle_id == cycle_key,
            PortalOrder.status == PortalOrderStatus.pending,
        )
        .first()
        is not None
    )
```

`update_product`：若改 `display_cycle_key`，必须存在于该商品 cycles，否则 `ValueError`。  
`remove_product_cycle`：若 `cycle.cycle_key == product.display_cycle_key`，`raise ValueError("cannot delete display cycle")`。  
`create_portal_order`：增加三个 snapshot 关键字参数并写入模型。

需要 `from darknight.db.models import Product, ProductCycle`（及已有 PortalOrder）。

- [ ] **Step 2: 快速冒烟（Python REPL 或临时脚本）**

启动 DB session，调用 `list_products` 应返回种子 3 条。

- [ ] **Step 3: Commit**

```bash
git add darknight/db/crud.py
git commit -m "feat(payment): add product CRUD helpers"
```

---

### Task 5: Admin Product API

**Files:**
- Create: `darknight/api/v1/routers/product.py`
- Modify: `darknight/api/v1/routers/__init__.py`
- Modify: `darknight/api/v1/api_router.py`

**Interfaces:**
- Consumes: Task 3 schemas + Task 4 crud
- Produces HTTP：
  - `GET /products`、`POST /product`、`GET|PUT|DELETE /product/{id}`
  - `POST /product/{id}/cycle`、`PUT|DELETE /product/{id}/cycle/{cycle_id}`

- [ ] **Step 1: 写 `product.py` router**

模式对齐 `node.py` / `user_template.py`：

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError

from darknight.db import Session, crud, get_db
from darknight.models.admin import Admin
from darknight.models.product import (
    ProductCreate,
    ProductCycleCreate,
    ProductCycleModify,
    ProductCycleResponse,
    ProductModify,
    ProductResponse,
)

router = APIRouter(tags=["Product"])


@router.get("/products", response_model=list[ProductResponse])
def list_products(db: Session = Depends(get_db), _: Admin = Depends(Admin.get_current)):
    return crud.list_products(db)


@router.post("/product", response_model=ProductResponse)
def add_product(
    body: ProductCreate,
    db: Session = Depends(get_db),
    _: Admin = Depends(Admin.check_sudo_admin),
):
    try:
        return crud.create_product(db, body)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Product slug or cycle_key already exists")


# GET/PUT/DELETE /product/{product_id} 同理
# cycle 子路由：删除前 has_pending_orders_for_* → 409
```

删除商品：

```python
if crud.has_pending_orders_for_product(db, product.slug):
    raise HTTPException(status_code=409, detail="Product has pending orders")
crud.remove_product(db, product)
return {}
```

- [ ] **Step 2: 注册**

`routers/__init__.py` 增加 `product`；`api_router.py` 的 `for router in (...):` 元组加入 `product.router`。

- [ ] **Step 3: 手工验收**

用 Admin token：

```bash
curl -H "Authorization: Bearer <admin>" http://localhost:<port>/<api_prefix>/products
```

Expected: 3 个种子商品，`is_listed: false`。

- [ ] **Step 4: Commit**

```bash
git add darknight/api/v1/routers/product.py darknight/api/v1/routers/__init__.py darknight/api/v1/api_router.py
git commit -m "feat(payment): add admin product CRUD API"
```

---

### Task 6: 公开 `/plans` + 下单/优惠券改读 DB

**Files:**
- Modify: `darknight/api/v1/routers/order.py`
- Modify: `darknight/services/payment/plans.py`（改为 DB 查询薄封装，或删除并由 order 直接用 crud）

**Interfaces:**
- Consumes: `crud.list_listed_products`、`crud.get_listed_cycle`
- Produces: `/plans` 返回完整双语字段；下单写入快照

- [ ] **Step 1: 重写 `list_plans`**

```python
@router.get("/plans", response_model=PlanCatalogResponse)
def list_plans(db: Session = Depends(get_db)):
    products = crud.list_listed_products(db)
    return PlanCatalogResponse(
        currency=get_app_config().paypal.currency,
        plans=[
            PlanResponse(
                plan_id=p.slug,
                name_zh=p.name_zh,
                name_en=p.name_en,
                category=p.category,
                features_zh=list(p.features_zh or []),
                features_en=list(p.features_en or []),
                display_cycle_id=p.display_cycle_key,
                sort_order=p.sort_order,
                cycles=[
                    PlanCycleResponse(
                        cycle_id=c.cycle_key,
                        price=c.price,
                        data_limit_gb=c.data_limit_gb,
                        duration_days=c.duration_days,
                        label_zh=c.label_zh,
                        label_en=c.label_en,
                    )
                    for c in sorted(p.cycles, key=lambda x: x.sort_order)
                    if c.is_listed
                ],
            )
            for p in products
        ],
    )
```

- [ ] **Step 2: 改 `preview_coupon` 与 `create_portal_order`**

用 `crud.get_listed_cycle(db, body.plan_id, body.cycle_id)`；失败 → 400。  
`create_portal_order` 调用：

```python
product, cycle = pair
order = crud.create_portal_order(
    db,
    order_id=generate_order_id(),
    user_id=dbuser.id,
    plan_id=product.slug,
    cycle_id=cycle.cycle_key,
    amount=round(cycle.price - discount, 2),
    currency=cfg.currency,
    paypal_order_id=None,
    coupon=coupon_code,
    discount=discount,
    snapshot_data_limit_gb=cycle.data_limit_gb,
    snapshot_duration_days=cycle.duration_days,
    snapshot_product_name=product.name_zh,
)
```

- [ ] **Step 3: 退役硬编码**

将 `plans.py` 的 `PLAN_CATALOG` / `get_plan_cycle` / `group_plan_catalog` 删除或改为转发到 crud（若还有 import）。全仓库 `rg "PLAN_CATALOG|get_plan_cycle|group_plan_catalog"` 清零。

- [ ] **Step 4: 验收**

```bash
curl http://localhost:<port>/<api_prefix>/plans
```

Expected: `plans: []`（种子未上架）。Admin 上架一个商品+周期后再 curl，应看到该商品及双语字段。

- [ ] **Step 5: Commit**

```bash
git add darknight/api/v1/routers/order.py darknight/services/payment/plans.py
git commit -m "feat(payment): serve plans and orders from product catalog"
```

---

### Task 7: 履约改读快照

**Files:**
- Modify: `darknight/services/payment/fulfillment.py`

**Interfaces:**
- Consumes: `order.snapshot_data_limit_gb`、`order.snapshot_duration_days`
- Produces: 不再依赖 `get_plan_cycle`

- [ ] **Step 1: 改 `fulfill_portal_order`**

```python
def fulfill_portal_order(db: Session, dbuser: User, order: PortalOrder) -> User:
    if order.snapshot_data_limit_gb is None or order.snapshot_duration_days is None:
        raise ValueError(
            f"Order {order.id} missing fulfillment snapshot "
            f"({order.plan_id}/{order.cycle_id})"
        )

    if dbuser.used_traffic:
        db.add(
            UserUsageResetLogs(
                user=dbuser,
                used_traffic_at_reset=dbuser.used_traffic,
            )
        )
    dbuser.used_traffic = 0
    dbuser.node_usages.clear()

    dbuser.data_limit = order.snapshot_data_limit_gb * 1024**3

    now_ts = int(datetime.utcnow().timestamp())
    base_expire = max(dbuser.expire or now_ts, now_ts)
    dbuser.expire = base_expire + order.snapshot_duration_days * 86400

    if dbuser.status != UserStatus.active:
        dbuser.status = UserStatus.active
        dbuser.last_status_change = datetime.utcnow()

    db.add(dbuser)
    db.commit()
    db.refresh(dbuser)
    return dbuser
```

移除对 `plans.get_plan_cycle` 的 import。

- [ ] **Step 2: Commit**

```bash
git add darknight/services/payment/fulfillment.py
git commit -m "feat(payment): fulfill portal orders from snapshots"
```

---

### Task 8: Admin 前端 API

**Files:**
- Create: `darknight/dashboard/src/api/product/types.ts`
- Create: `darknight/dashboard/src/api/product/index.ts`

**Interfaces:**
- Produces: `useProductsQuery`、`useProductMutations`（create/update/delete product + cycle CRUD + invalidate `['products']`）

- [ ] **Step 1: types**

```typescript
export interface ProductCycle {
  id: number
  cycle_key: string
  label_zh: string
  label_en: string
  price: number
  data_limit_gb: number
  duration_days: number
  is_listed: boolean
  sort_order: number
}

export interface Product {
  id: number
  slug: string
  name_zh: string
  name_en: string
  category: 'period' | 'traffic'
  features_zh: string[]
  features_en: string[]
  display_cycle_key: string
  sort_order: number
  is_listed: boolean
  created_at: string
  updated_at: string
  cycles: ProductCycle[]
}

export type ProductCreateBody = Omit<Product, 'id' | 'created_at' | 'updated_at' | 'cycles'> & {
  cycles: Omit<ProductCycle, 'id'>[]
}
```

- [ ] **Step 2: hooks（对齐 `api/node/index.ts`）**

```typescript
export const productsQueryKey = ['products'] as const

export function useProductsQuery() {
  return useQuery({
    queryKey: productsQueryKey,
    queryFn: () => http<Product[]>('/products'),
    refetchOnWindowFocus: false
  })
}

export function useProductMutations() {
  const queryClient = useQueryClient()
  const invalidate = () => queryClient.invalidateQueries({ queryKey: productsQueryKey })
  // addProduct POST /product
  // updateProduct PUT /product/:id
  // deleteProduct DELETE /product/:id
  // addCycle POST /product/:id/cycle
  // updateCycle PUT /product/:id/cycle/:cycleId
  // deleteCycle DELETE /product/:id/cycle/:cycleId
  return { addProduct, updateProduct, deleteProduct, addCycle, updateCycle, deleteCycle }
}
```

- [ ] **Step 3: Commit**

```bash
git add darknight/dashboard/src/api/product
git commit -m "feat(dashboard): add admin product API client"
```

---

### Task 9: Admin Product 页面

**Files:**
- Create: `darknight/dashboard/src/views/admin/Product/index.vue`
- Create: `darknight/dashboard/src/views/admin/Product/components/ProductsTable.vue`
- Create: `darknight/dashboard/src/views/admin/Product/components/ProductDialog.vue`
- Modify: `darknight/dashboard/src/router/admin.ts`
- Modify: `darknight/dashboard/src/layout/components/Menu/index.vue`
- Modify: `darknight/dashboard/src/locales/zh.json`、`en.json`、`ru.json`、`fa.json`

**Interfaces:**
- Consumes: Task 8 hooks
- Produces: `/admin/products` 可列表、新建/编辑、上下架、删商品/周期

- [ ] **Step 1: 路由与菜单**

`admin.ts` children 增加：

```typescript
{
  path: 'products',
  name: 'products',
  component: () => import('@/views/admin/Product/index.vue'),
  meta: { title: 'header.productSettings', icon: 'ShoppingBag', authType: 'admin' }
}
```

`Menu/index.vue`：`import { ..., ShoppingBag } from 'lucide-vue-next'`，`iconMap.ShoppingBag = ShoppingBag`。

四语言增加键，例如：

```json
"header.productSettings": "商品",
"products.pageTitle": "商品管理",
"products.create": "新建商品",
"products.deleteConfirm": "确定删除该商品？",
"products.pendingBlock": "存在未完成订单，无法删除"
```

（en/ru/fa 语义对等。）

- [ ] **Step 2: 列表页 + Table**

对齐 `Node/index.vue`：标题、新建按钮、`ProductsTable`（列：sort_order、slug、name_zh、category、cycles.length、is_listed Switch、编辑/删除）。  
Switch 变更立即 `updateProduct({ id, is_listed })`；失败 toast。  
删除走 `useConfirm`；捕获 409 toast `products.pendingBlock`。

- [ ] **Step 3: ProductDialog**

表单字段：slug、name_zh/en、category select、sort_order、is_listed、display_cycle_key、features_zh/en 可增删行、cycles 子表（可增删行）。  
新建时 cycles 一并 POST；编辑时商品字段 PUT，周期变更可逐条 add/update/delete（或整单保存策略二选一，优先：编辑页保存商品字段 + 周期子表分别 mutation，实现更清晰）。

- [ ] **Step 4: 前端构建**

```bash
cd darknight/dashboard
npm run build
```

Expected: 成功。

- [ ] **Step 5: Commit**

```bash
git add darknight/dashboard/src/views/admin/Product darknight/dashboard/src/router/admin.ts darknight/dashboard/src/layout/components/Menu/index.vue darknight/dashboard/src/locales
git commit -m "feat(dashboard): add admin products management page"
```

---

### Task 10: 门户购买改读双语目录

**Files:**
- Modify: `darknight/dashboard/src/api/portal/orders.ts`
- Modify: `darknight/dashboard/src/views/portal/Buy/plans.ts`
- Modify: `darknight/dashboard/src/views/portal/Buy/usePlanCatalog.ts`
- Modify: `darknight/dashboard/src/views/portal/Buy/index.vue`
- Modify: `darknight/dashboard/src/views/portal/Buy/Configure.vue`（及任何引用 `labelKey` / `PLAN_META` / `getPlanMeta` / `hasMeta` 的文件）

**Interfaces:**
- Consumes: 扩展后的 `/plans`
- Produces: 门户无硬编码 meta；按 locale 显示 name/features/cycle label

- [ ] **Step 1: 扩展 `orders.ts` 类型**

```typescript
export interface PlanCycle {
  cycle_id: string
  price: number
  data_limit_gb: number
  duration_days: number
  label_zh: string
  label_en: string
}

export interface Plan {
  plan_id: string
  name_zh: string
  name_en: string
  category: 'period' | 'traffic'
  features_zh: string[]
  features_en: string[]
  display_cycle_id: string
  sort_order: number
  cycles: PlanCycle[]
}
```

- [ ] **Step 2: 精简 `plans.ts`**

删除 `PLAN_META` / `getPlanMeta`。保留：

```typescript
export type PlanFilter = 'all' | 'period' | 'traffic'
export type PlanCategory = 'period' | 'traffic'
export function formatPrice(amount: number): string { return amount.toFixed(2) }
export function currencySymbol(currency: string): string {
  return currency === 'USD' ? '$' : `${currency} `
}
export function pickLocale<T>(locale: string, zh: T, en: T): T {
  return locale.toLowerCase().startsWith('zh') ? zh : en
}
```

- [ ] **Step 3: 重写 `usePlanCatalog`**

```typescript
export interface PricedCycle {
  id: string
  label: string
  price: number
  dataLimitGb: number
  durationDays: number
}

export interface PricedPlan {
  id: string
  name: string
  category: PlanCategory
  features: string[]
  displayCycleId: string
  sortOrder: number
  cycles: PricedCycle[]
}

export function usePlanCatalog() {
  const { locale } = useI18n()
  const query = useQuery({ queryKey: planCatalogQueryKey, queryFn: fetchPlanCatalog, ... })

  const plans = computed<PricedPlan[]>(() => {
    const catalog = query.data.value
    if (!catalog) return []
    const loc = locale.value
    return [...catalog.plans]
      .sort((a, b) => a.sort_order - b.sort_order)
      .map((plan) => ({
        id: plan.plan_id,
        name: pickLocale(loc, plan.name_zh, plan.name_en),
        category: plan.category,
        features: pickLocale(loc, plan.features_zh, plan.features_en),
        displayCycleId: plan.display_cycle_id,
        sortOrder: plan.sort_order,
        cycles: plan.cycles.map((c) => ({
          id: c.cycle_id,
          label: pickLocale(loc, c.label_zh, c.label_en),
          price: c.price,
          dataLimitGb: c.data_limit_gb,
          durationDays: c.duration_days
        }))
      }))
  })
  // getPlan / getCycle / filterPlans 同前；删除 hasMeta
}
```

- [ ] **Step 4: 更新页面**

`index.vue`：卖点用 `plan.features` 直接渲染（不再 `t(featureKey)`）；周期标签用 `displayCycle(plan).label`。  
`Configure.vue`：周期选项显示 `cycle.label` 而非 `t(cycle.labelKey)`。  
全库搜索 `PLAN_META|getPlanMeta|labelKey|hasMeta|featureKeys|getCycleLabelKey` 并清零。

- [ ] **Step 5: 构建**

```bash
cd darknight/dashboard
npm run build
```

Expected: PASS。

- [ ] **Step 6: Commit**

```bash
git add darknight/dashboard/src/api/portal/orders.ts darknight/dashboard/src/views/portal/Buy
git commit -m "feat(dashboard): drive portal buy catalog from API copy"
```

---

### Task 11: 端到端验收

**Files:** 无新文件（文档可选更新）

- [ ] **Step 1: 按 spec 验收清单操作**

1. Admin 打开 `/admin/products`，见 3 个下架种子。  
2. 编辑 `100g`：确认中英卖点与截图一致；上架商品 + `yearly` 周期。  
3. 门户 `/portal/buy`：只见 100G 卡，卖点与价格正确；切换 en 见英文。  
4. 下架后门户消失。  
5. 造一笔 pending 订单后删商品 → 409。  
6. 关闭订单后再删或保持种子：可上架完整购买（支付环境允许时验证履约流量/天数 = 快照）。

- [ ] **Step 2: 最终提交（若有零散修正）**

```bash
git status
# 如有修复则 commit
```

---

## Spec Coverage Checklist

| Spec 项 | Task |
|---------|------|
| Product + ProductCycle 模型 | 1 |
| 订单快照列 | 1–2 |
| 种子默认下架 + 中英卖点 | 2 |
| Admin CRUD API + pending 409 + 级联 | 4–5 |
| `/plans` / 下单 / 优惠券读 DB | 6 |
| 履约读快照 | 7 |
| Admin UI | 8–9 |
| 门户双语改造、去硬编码 | 10 |
| 验收清单 | 11 |
| 非目标（模板/优惠券页/PayPal 改链路） | 不实现 |

## Self-Review Notes

- 无 pytest：验收以 curl + UI + `npm run build` 为准（与本仓库近期 plan 一致）。  
- `display_cycle_key` 与公开 API 的 `display_cycle_id` 并存：DB/Admin 用 key，公开响应字段名保持 `display_cycle_id` 以贴近旧前端。  
- 类型名 `PricedCycle.id` 改为 `string`（不再绑死旧 `BillingCycleId` union），以支持自定义 cycle_key。
