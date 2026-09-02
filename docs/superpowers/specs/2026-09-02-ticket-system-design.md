# 工单系统（门户 + 管理端）设计

日期：2026-09-02  
状态：已确认方案，待用户审阅 spec  
前置：`2026-08-31-portal-shell-and-pages-design.md`（门户壳层）；`2026-09-01-admin-product-catalog-design.md`（Admin CRUD 模式参考）

## 背景

门户路由 `/portal/tickets`（`portal-tickets`）与菜单、仪表盘快捷入口、文档引导文案已存在，但页面仍为 Placeholder，后端无数据模型与 API。管理端无工单管理能力。

用户提供了外部参考 UI（工单历史列表 + 新建工单弹窗），实际实现须对齐本项目现有风格：Tailwind + shadcn、紫 primary、`rounded-2xl border bg-card` 白卡片、门户表格对齐 `Orders`、Admin 对齐 `Product` / `User`。

## 已确认决策

| 项 | 决策 |
|---|---|
| 整体架构 | **方案 A**：门户列表 + 详情页 + 对话线程；Admin 列表 + 处理 Dialog |
| 工单等级 | **四档**：`low`（低）/ `normal`（中）/ `high`（高）/ `urgent`（紧急） |
| 附件 | 首版不做文件上传 |
| 通知 | 首版不做邮件/Telegram 推送 |
| 指派 | 首版不做管理员指派，所有 Admin 均可查看与回复 |
| 技术栈 | 后端 FastAPI + SQLAlchemy；前端 Vue 3 + tanstack query + shadcn |
| 鉴权 | 门户 `PortalUser.get_current`；Admin 读写在现有 admin 鉴权下，写操作对齐 `check_sudo_admin` |

## 一、数据模型

### `tickets`

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | Integer PK | 自增主键 |
| `user_id` | Integer FK → `users.id` | 提交用户 |
| `subject` | String(256) | 主题，必填 |
| `priority` | Enum | `low` / `normal` / `high` / `urgent`，默认 `normal` |
| `status` | Enum | `open` / `pending` / `resolved` / `closed`，默认 `open` |
| `created_at` | DateTime | 创建时间 |
| `updated_at` | DateTime | 最后更新时间 |
| `last_reply_at` | DateTime nullable | 最后一条回复时间；创建时等于 `created_at` |

索引：`user_id`、`status`、`priority`、`last_reply_at`。

### `ticket_replies`

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | Integer PK | 自增主键 |
| `ticket_id` | Integer FK → `tickets.id` ON DELETE CASCADE | 所属工单 |
| `author_type` | Enum | `user` / `admin` |
| `author_id` | Integer | `users.id` 或 `admins.id`（按 `author_type` 解释） |
| `content` | Text | 回复正文，必填，最长 10000 字符 |
| `created_at` | DateTime | 回复时间 |

索引：`ticket_id`、`created_at`。

### 状态语义

| 状态 | 含义 | 门户展示 |
|---|---|---|
| `open` | 新建或用户刚回复，待管理员处理 | 待处理 |
| `pending` | 管理员已回复，等待用户 | 等待回复 |
| `resolved` | 管理员标记已解决 | 已解决 |
| `closed` | 已关闭，不可再回复 | 已关闭 |

### 状态流转

```
用户创建 ──► open
管理员首次回复 ──► pending
用户回复 ──► open
管理员标记已解决 ──► resolved
管理员关闭 / 用户确认关闭 ──► closed
```

规则：

- 创建工单时写入首条 `ticket_replies`（`author_type=user`），内容与表单「消息」字段一致
- 用户回复：仅当 `status ∈ {open, pending}` 且工单属于当前用户
- 管理员回复：任意非 `closed` 状态均可回复；回复后若原状态为 `open` 则改为 `pending`
- 管理员可将 `open` / `pending` / `resolved` 改为 `resolved` 或 `closed`
- 用户可将 `resolved` 改为 `closed`（确认问题已解决）
- `closed` 后禁止追加回复

## 二、API

实现落点：`darknight/models/ticket.py`、`darknight/db/models.py`（ORM）、`darknight/db/crud.py`、`darknight/api/v1/routers/ticket.py`；在 `api_router.py` 注册。

### 门户（`PortalUser.get_current`）

| 方法 | 路径 | 作用 |
|---|---|---|
| `GET` | `/tickets` | 当前用户工单列表，按 `last_reply_at` 降序 |
| `POST` | `/tickets` | 创建工单（`subject`, `priority`, `content`） |
| `GET` | `/tickets/{id}` | 工单详情 + 回复列表（仅本人） |
| `POST` | `/tickets/{id}/replies` | 用户追加回复（body: `content`） |
| `PATCH` | `/tickets/{id}` | 用户将 `resolved` → `closed` |

### 管理端（Admin 鉴权）

| 方法 | 路径 | 作用 |
|---|---|---|
| `GET` | `/admin/tickets` | 全站列表；query：`status?`, `priority?`, `offset?`, `limit?` |
| `GET` | `/admin/tickets/{id}` | 详情 + 回复 + 用户信息（username） |
| `PATCH` | `/admin/tickets/{id}` | 更新 `status` / `priority`（`check_sudo_admin`） |
| `POST` | `/admin/tickets/{id}/replies` | 管理员回复（`check_sudo_admin`） |

### Pydantic Schema（概要）

- `TicketCreate`: `subject` (1–256), `priority`, `content` (1–10000)
- `TicketReplyCreate`: `content` (1–10000)
- `TicketModify` (admin): `status?`, `priority?`
- `TicketListItem`: `id`, `subject`, `priority`, `status`, `created_at`, `last_reply_at`
- `TicketDetail`: 列表字段 + `replies[]`（含 `author_type`, `content`, `created_at`；admin 详情额外含 `username`）
- `AdminTicketListItem`: 列表字段 + `username`

### 错误码

| 场景 | 状态码 |
|---|---|
| 工单不存在 | 404 |
| 门户用户访问他人工单 | 404（不泄露存在性） |
| 已关闭工单回复 | 400 |
| 非法状态流转 | 400 |
| 字段校验失败 | 422 |

## 三、门户前端

路径：`darknight/dashboard/src/views/portal/Tickets/`

### 文件结构

```
Tickets/
├── index.vue                    # 工单历史列表
├── Detail.vue                   # 工单详情 + 回复线程
└── components/
    └── CreateTicketDialog.vue   # 新建工单弹窗
```

路由调整（`router/portal.ts`）：

| 路由名 | 路径 | 组件 |
|---|---|---|
| `portal-tickets` | `tickets` | `Tickets/index.vue` |
| `portal-ticket-detail` | `tickets/:ticketId` | `Tickets/Detail.vue` |

API 客户端：`darknight/dashboard/src/api/portal/tickets.ts`

### 列表页 `index.vue`

对齐 `Orders/index.vue` 视觉与交互：

- 容器：`max-w-6xl`
- 顶栏：左侧标题「工单历史」；右侧主按钮「新的工单」
- 表格列：`#`（id）/ 主题 / 工单级别 / 工单状态 / 创建时间 / 最后回复 / 操作（查看）
- 级别与状态用 `Badge`，颜色映射：
  - `low` → secondary；`normal` → outline；`high` → default；`urgent` → destructive
  - `open` → default；`pending` → secondary；`resolved` → outline；`closed` → muted
- 加载：`Skeleton`；空态：居中文案 + 引导创建按钮
- 点击「查看」或行 → `portal-ticket-detail`
- 「新的工单」打开 `CreateTicketDialog`；创建成功后刷新列表并可选跳转详情

### 新建弹窗 `CreateTicketDialog.vue`

对齐 shadcn `Dialog`（参考 Admin `ProductDialog`）：

- 字段：主题（`Input`）、工单等级（`Select` 四档）、消息（`Textarea`）
- 校验：三者均必填；提交 `POST /tickets`
- 按钮：取消 / 确认；提交中 disabled + loading

### 详情页 `Detail.vue`

对齐 `Orders/Detail.vue` 布局习惯：

- 顶部：返回按钮 + 主题 + 级别/状态 Badge
- 中部：回复时间线（用户靠右或浅色底，管理员靠左或带标识）
- 底部：回复区（`status === closed` 时隐藏）
- `resolved` 时显示「确认关闭」按钮（`PATCH` → `closed`）
- 使用 `useQuery` 拉详情；`useMutation` 发回复

## 四、管理端前端

路径：`darknight/dashboard/src/views/admin/Ticket/`

### 文件结构

```
Ticket/
├── index.vue
└── components/
    ├── TicketsTable.vue
    ├── TicketFilters.vue
    └── TicketDetailDialog.vue
```

路由（`router/admin.ts`）：`/admin/tickets`，`meta.title` 为 i18n key，图标 `Headset`。

API 客户端：`darknight/dashboard/src/api/ticket/index.ts`、`types.ts`

### 列表页

对齐 `User/index.vue` + `Product/index.vue`：

- 筛选：`TicketFilters` — 状态下拉、优先级下拉、（可选）关键词搜主题
- 表格列：ID、用户名、主题、级别、状态、创建时间、最后回复、操作（处理）
- 「处理」打开 `TicketDetailDialog`

### 处理弹窗 `TicketDetailDialog.vue`

- 展示工单信息与完整回复线程
- 底部：回复 `Textarea` + 发送
- 侧栏或顶栏：状态下拉、优先级下拉，变更即 `PATCH`
- 快捷按钮：「标记已解决」「关闭工单」

## 五、i18n

扩展 `zh.json` / `en.json`：

- `portal.tickets.*` — 列表、创建、详情、级别、状态、空态、操作文案
- `admin.tickets.*` — 菜单、筛选、表格列、处理弹窗
- 级别：`low` / `normal` / `high` / `urgent` 各中英文标签
- 状态：`open` / `pending` / `resolved` / `closed` 各中英文标签

现有 `portal.menu.tickets` 等 key 保留，新增细粒度 key。

## 六、数据库迁移

- Alembic migration：创建 `tickets`、`ticket_replies` 表及索引
- 无种子数据要求

## 七、验收标准

### 门户

- `/portal/tickets` 不再显示 Placeholder
- 可创建工单（主题 + 四档等级 + 消息），列表正确展示
- 可进入详情查看对话、追加回复
- `resolved` 工单可确认关闭；`closed` 不可回复
- 样式与 `Orders`、Dashboard 卡片风格一致，无 Element 组件

### 管理端

- `/admin/tickets` 可查看全站工单，支持状态/优先级筛选
- 可查看对话、回复、修改状态与优先级
- 管理员回复后工单状态按规则更新

### 后端

- 门户用户只能访问自己的工单
- 状态流转符合第四节规则
- API 在 `api_router` 注册并可被前端正常调用

## 八、非目标（本 spec）

- 附件上传
- 邮件 / Telegram / Webhook 通知
- 工单指派、SLA、自动关闭定时任务
- 用户评分 / 满意度
- 富文本编辑器（首版纯文本 `Textarea`）

## 九、实施顺序建议

1. 后端：ORM + migration + Pydantic + crud + router + 注册
2. 门户：API 客户端 + 列表页 + 创建弹窗
3. 门户：详情页 + 回复
4. Admin：API 客户端 + 路由 + 列表 + 筛选 + 处理弹窗
5. i18n 补全 + 联调验收
