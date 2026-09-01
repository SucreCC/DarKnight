# 管理端商品目录与门户购买改造设计

日期：2026-09-01  
状态：已确认，待写实现计划  

## 背景

当前商城套餐为硬编码：后端 `PLAN_CATALOG`（价格/流量/天数）与前端 `PLAN_META`（名称/分类/卖点 i18n key）。管理后台无商品 CRUD，改价或改文案必须改代码并部署。

目标：引入可管理的商品目录，支持新增/编辑/上下架/删除，并让门户购买完全改为读取数据库商品。

## 已确认决策

| 项 | 决策 |
|---|---|
| 模型 | 全新 DB 商品（非继续维护硬编码） |
| 履约 | 方案 A：周期自带 `data_limit_gb` + `duration_days` |
| 结构 | 一商品多周期（价格/天数等可不同） |
| 删除 | 可下架 + 可硬删；存在 `pending` 订单引用时禁止硬删（409） |
| 范围 | 管理后台 CRUD + 门户购买一并切到 DB |
| 种子 | 导入现有 3 套餐及中英卖点，**全部默认下架** |
| 文案 | 名称与卖点支持中英双语纯文本（非 i18n key） |
| 架构 | `Product` + `ProductCycle` 两表 |

## 一、数据模型

### `products`

| 字段 | 说明 |
|---|---|
| `id` | 自增主键 |
| `slug` | 唯一稳定标识（如 `100g`；迁移沿用旧 `plan_id`） |
| `name_zh` / `name_en` | 卡片标题 |
| `category` | `period` \| `traffic`（门户筛选） |
| `features_zh` / `features_en` | JSON 字符串数组（卖点列表） |
| `display_cycle_key` | 列表页主价格对应的 `cycle_key` |
| `sort_order` | 展示排序 |
| `is_listed` | 商品级上架 |
| `created_at` / `updated_at` | 时间戳 |

### `product_cycles`

| 字段 | 说明 |
|---|---|
| `id` | 自增主键 |
| `product_id` | FK → `products` |
| `cycle_key` | 同商品内唯一（如 `monthly` / `yearly` / `two_years`） |
| `label_zh` / `label_en` | 周期展示名 |
| `price` | 标价（货币沿用 `paypal.currency`） |
| `data_limit_gb` | 履约流量（GB） |
| `duration_days` | 履约天数 |
| `is_listed` | 周期级上架 |
| `sort_order` | 配置页周期排序 |

唯一约束：`products.slug`；`(product_id, cycle_key)`。

### 可见与可买规则

- 门户展示：`product.is_listed` 且至少存在一个 `cycle.is_listed`
- 可下单：商品与所选周期均 `is_listed`
- `display_cycle_key` 必须属于该商品的某个周期

### `portal_orders` 调整

- 保留 `plan_id` / `cycle_id` 字段名，语义改为 `product.slug` + `cycle_key`（兼容历史订单与前端）
- 新增履约快照：`snapshot_data_limit_gb`、`snapshot_duration_days`、`snapshot_product_name`（下单时写入）
- 履约优先读快照，避免后台改商品影响已下单用户

### 校验

- `price > 0`，`data_limit_gb > 0`，`duration_days > 0`
- `slug` / `(product_id, cycle_key)` 冲突 → 409
- 硬删时若存在引用该商品或周期的 `pending` 订单 → 409
- 删除商品时级联删除其周期；删除作为 `display_cycle_key` 的周期前须先改商品的展示周期，否则 400

## 二、API

### 管理端（Admin 鉴权；写操作对齐现有 Node 的 `check_sudo_admin`）

路径风格与现有 `/node`、`/nodes` 一致（由应用统一挂载 API 前缀）：

| 方法 | 路径 | 作用 |
|---|---|---|
| `GET` | `/products` | 列表（含周期，含已下架） |
| `POST` | `/product` | 新建（可顺带 cycles） |
| `GET` | `/product/{id}` | 详情 |
| `PUT` | `/product/{id}` | 更新商品字段 |
| `DELETE` | `/product/{id}` | 硬删（pending 保护；级联周期） |
| `POST` | `/product/{id}/cycle` | 新增周期 |
| `PUT` | `/product/{id}/cycle/{cycle_id}` | 更新周期 |
| `DELETE` | `/product/{id}/cycle/{cycle_id}` | 硬删周期（pending 保护） |

实现落点：新建 router（如 `api/v1/routers/product.py`）、Pydantic schemas、`crud` 方法、ORM 模型；在 routers `__init__` 注册。

### 公开 / 门户

| 方法 | 路径 | 变化 |
|---|---|---|
| `GET` | `/plans` | 改为读 DB 上架商品；返回 slug 作 `plan_id`、`cycle_key` 作 `cycle_id`，并附带中英 name/features/cycle labels |
| `POST` | `/orders` | 校验双上架；写入金额与履约快照 |

### 履约

- `fulfill_portal_order` 改为使用订单快照的流量/天数
- 移除运行时对硬编码 `PLAN_CATALOG` 的依赖（种子数据可暂存于迁移脚本）

## 三、管理后台 UI

- 路由：`/admin/products`，侧栏新增「商品」入口
- 模式对齐 Node：列表 Table + Dialog/表单 + `useQuery` / `useMutation`
- 列表列：排序、slug、名称（中）、分类、周期数、上架、操作（编辑 / 上下架 / 删除）
- 表单：基本信息 + 中英卖点可增删行 + 周期子表（增删改）
- 上架 Switch 可即时 `PUT`；删除二次确认；409 以 Toast 展示

## 四、门户购买改造

- 删除对前端 `PLAN_META` 硬编码及卖点 i18n key 的运行时依赖
- `usePlanCatalog` 完全消费 `GET /plans`
- 按当前语言选择 `name_*` / `features_*` / cycle `label_*`
- 列表卡与配置页视觉保持现有风格；筛选继续用 `category`
- 种子默认全下架 → 部署后需管理员在后台上架后商城才有商品

## 五、迁移与种子

Alembic 迁移：

1. 建 `products`、`product_cycles`
2. 为 `portal_orders` 增加快照列（可空）
3. 插入现有目录（全部 `is_listed=false`）：

| slug | category | display | cycles |
|---|---|---|---|
| `100g` | period | yearly | yearly 1.99 / 100GB / 365d；two_years 2.99 / 100GB / 730d |
| `1024g` | traffic | quarterly | quarterly 2.49 / 1024GB / 90d |
| `2048g` | traffic | monthly | monthly 0.99 / 2048GB / 30d |

卖点中英文本从现有 `zh.json` / `en.json` 的 `portal.buy.feature.*` 导入对应内容。

历史 `pending`/`paid` 订单：尽量按旧 `plan_id`/`cycle_id` 回填快照；无法匹配则履约时明确失败并记日志。

## 六、验收

1. 后台可新建商品与多周期，上架后门户可见且可买  
2. 修改中英卖点/价格后门户即时反映  
3. 下架后门户不可见且无法下单  
4. 有 pending 订单时硬删被拒；无冲突时可删  
5. 支付成功后用户流量与到期天数与下单快照一致  
6. 种子导入 3 个旧套餐，默认下架  

## 七、非目标

- 不绑定 `UserTemplate` / 不按模板改 inbounds  
- 不在本需求中做优惠券管理页  
- 不改 PayPal 支付链路本身（仅换商品数据源与履约读快照）  
- 不做 ru/fa 商品文案（仅 zh/en；其他语言可回退 en）  
- 不引入库存、限购、自动续费  

## 八、关键文件（预期）

| 区域 | 路径 |
|---|---|
| ORM | `darknight/db/models.py` |
| CRUD | `darknight/db/crud.py` |
| Schemas | `darknight/models/product.py`（新建） |
| Admin API | `darknight/api/v1/routers/product.py`（新建） |
| Plans/Orders | `darknight/api/v1/routers/order.py`、`models/order.py` |
| 履约 | `darknight/services/payment/fulfillment.py` |
| 硬编码目录 | `darknight/services/payment/plans.py`（退役） |
| Admin UI | `dashboard/src/views/admin/Product/`、`router/admin.ts` |
| Portal | `dashboard/src/views/portal/Buy/`（`plans.ts` / `usePlanCatalog.ts` 等） |
