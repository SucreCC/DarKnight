# 前端重写规划方案（Vue 3 + Vite + Element Plus）

- 日期：2026-08-18
- 范围：`darknight/dashboard`（前端管理面板）—— **整体重写**（从 React 迁到 Vue 3）
- 技术方向（已确认）：**Vue 3 + Vite + Element Plus + Pinia + Vue Router + vee-validate/zod + i18next(vue-i18n)**
- 交付物：本规划文档 + 实施计划 + 完整重写

> 说明：原 React + Ant Design 方案已废弃，本文件为最新方案。

---

## 1. 为什么重写（现状问题回顾）

现有 React 前端存在：半成品目录重构留下的死代码、巨型文件（`HostsDialog` 1295 行、`UserDialog` 838 行、`UsersTable` 800 行）、`Dashboard` 巨页、状态管理三套混用（zustand + 多个"Context"实为 store + react-query）、命名不一致（Modal/Dialog）。用户决定整体切换到 Vue 3 + Element Plus，从零重写以获得清晰结构与内置表格/表单能力。

---

## 2. 后端托管约束（必须满足）

`darknight/dashboard/__init__.py` 的行为决定了重写的硬约束：

- 后端在 `darknight/dashboard/` 目录执行：`npm run build -- --outDir build --assetsDir statics`。
  → Vue 项目**必须仍位于 `darknight/dashboard/`**，`package.json` 的 `build` 脚本为 `vite build`（可接受追加的 `--outDir`/`--assetsDir` 参数）。
- 构建产物 `build/index.html` + `build/statics/*`，以 `StaticFiles(html=True)` 挂载（纯静态 SPA）。
  → **必须用 hash 路由**（`createWebHashHistory`），否则刷新子路径会 404。
- 通过环境变量 `VITE_BASE_API` 注入 API base（默认 `/api/v1/`）。
  → HTTP 客户端读取 `import.meta.env.VITE_BASE_API`，默认 `/api/v1/`。
- 开发期 `vite.config.ts` 保留 `/api/v1` 代理到后端（默认 `http://127.0.0.1:33100`）。

---

## 3. 完整 API 面（重写需忠实还原）

**Auth**
- `POST /admin/token`（表单登录，返回 access_token）
- `GET /admin`（当前管理员信息 / 路由守卫校验）

**Users**
- `GET /users`（query: search, limit, offset, sort, status）
- `POST /user`（创建）
- `PUT /user/{username}`（编辑）
- `DELETE /user/{username}`（删除）
- `POST /users/reset`（重置所有用量）
- `POST /user/{username}/reset`（重置单用户用量）
- `POST /user/{username}/revoke_sub`（撤销订阅）
- `GET /user/{username}/usage`（用量图表数据，query: start,end）
- `GET /inbounds`（可选 inbounds 列表）

**Nodes**
- `GET /nodes`、`POST /node`、`PUT /node/{id}`、`DELETE /node/{id}`
- `POST /node/{id}/reconnect`
- `GET /nodes/usage`（query: start,end）

**Hosts**
- `GET /hosts`、`PUT /hosts`

**Core**
- `GET /core`（version, started, logs_websocket）
- `GET /core/config`、`PUT /core/config`、`POST /core/restart`
- 日志：WebSocket（`logs_websocket`）

**System**
- `GET /system`（统计：内存/带宽/在线数等）

---

## 4. 目标技术栈

| 层 | 选型 | 说明 |
|---|---|---|
| 框架 | **Vue 3**（`<script setup>` + TS） | 组合式 API |
| 构建 | **Vite** | 保留，配 hash 路由与 `/api/v1` 代理 |
| UI 库 | **Element Plus** | `el-table`/`el-form`/`el-dialog` 等内置，消灭巨型手写 |
| 图标 | `@element-plus/icons-vue` | |
| 状态 | **Pinia** | UI 状态 + 轻量数据缓存 |
| 数据请求 | `@tanstack/vue-query`（可选）或 Pinia + composable | 首选 vue-query 管服务端数据 |
| 表单校验 | Element Plus 内置 rules（复杂处配 **zod**） | |
| 路由 | **Vue Router**（hash 模式） | |
| i18n | **vue-i18n** | 迁移现有 locales |
| HTTP | `ofetch`（保留）封装到 `shared/api/http.ts` | 复用现有 token 注入逻辑 |
| 图表 | ECharts（`vue-echarts`）或沿用 apexcharts(vue3) | 用量图 |
| JSON 编辑器 | `@guolao/vue-monaco-editor` 或 codemirror | 核心配置编辑 |
| 主题 | Element Plus 暗色主题（`dark` class 切换） | 明暗切换 |

---

## 5. 目标目录结构（feature-based）

```
darknight/dashboard/
├── index.html
├── package.json                 # build: vite build
├── vite.config.ts               # hash 由 router 决定；保留 /api/v1 代理
├── tsconfig.json
└── src/
    ├── main.ts                  # 应用入口：app.use(pinia/router/i18n/ElementPlus)
    ├── App.vue                  # <router-view/>
    ├── app/
    │   ├── router.ts            # createRouter + createWebHashHistory + 守卫
    │   └── i18n.ts
    ├── layouts/
    │   └── DashboardLayout.vue  # el-container: 侧栏菜单 + 顶栏 + <router-view/>
    ├── pages/                   # 路由页（薄，组合 features）
    │   ├── LoginPage.vue
    │   ├── UsersPage.vue
    │   ├── NodesPage.vue
    │   ├── HostsPage.vue
    │   └── SettingsPage.vue
    ├── features/
    │   ├── users/{api,components,composables,store.ts,types.ts}
    │   ├── nodes/{...}
    │   ├── hosts/{...}
    │   └── settings/{...}
    ├── components/              # 通用：StatusTag、UsageChart、ThemeToggle、LanguageSwitch...
    ├── shared/
    │   ├── api/http.ts          # ofetch + token 注入（迁移现有 http.ts）
    │   ├── lib/                 # formatByte、dateFormatter、color 等
    │   ├── constants/
    │   └── types/
    ├── locales/                 # vue-i18n 资源
    └── styles/                  # 全局样式 + Element 主题变量
```

---

## 6. 状态管理

- 服务端数据：`@tanstack/vue-query` composables，就近放 `features/*/api/`；查询键每模块集中。
- UI 状态：Pinia store（每模块一个：弹窗开关、当前选中、筛选/分页）。
- 认证：`shared/api/http.ts` 注入 token；`app/router.ts` 守卫用 `GET /admin` 校验。

---

## 7. 关键功能点还原清单

- **登录**：`/admin/token` 表单登录，存 token（localStorage），失败提示。
- **用户表**：分页/筛选（search/status/sort）/状态标签/用量进度/在线状态/每行操作（编辑、删除、二维码、重置用量、撤销订阅、复制订阅链接）。
- **用户表单**：用户名、协议(proxies: vmess/vless/trojan/shadowsocks)、inbounds 选择、流量限额 + 重置策略、到期(expire)/on_hold、备注。
- **节点**：列表、增删改、重连、用量图。
- **主机**：`/hosts` 多字段配置（remark、address、port、sni、host、path、security(tls/none/inbound_default)、alpn、fingerprint、fragment、noise、mux、sockopt、allowinsecure 等），按区块拆分。
- **核心设置**：查看版本/状态、编辑 xray 配置 JSON、重启、日志 WebSocket。
- **统计**：`/system` 概览卡片。
- **i18n + 明暗主题**：保留。

---

## 8. 分阶段（详见 plan 文档）

阶段 A 脚手架 → B 基础设施(http/auth/router/layout/theme/i18n) → C Users → D Nodes → E Hosts → F Settings/Stats → G 构建验证与清理旧 React 代码。

---

## 9. 风险与策略

- **风险：整体重写期间面板不可用** → 先在 `dashboard/` 保留旧 React `build/` 产物；新代码就绪并构建通过后再切换（或直接替换 `src/` 但确保 `npm run build` 始终可产出可用产物后再交付）。
- **风险：hash 路由约束** → 全程用 `createWebHashHistory`。
- **风险：主机表单字段多** → 读旧 `HostsDialog` 逐字段还原，用 `el-form` + 分区块子组件（每块 < 300 行）。
- **回滚**：旧 React `src/` 在 git 历史中，可回退。
```