# 前端重写 实施计划（Vue 3 + Element Plus）

> 本计划替代原 React+AntD 计划。按"阶段(Phase)→任务(Task)"组织，每阶段结束需 `npm run build` 通过 + `npm run dev` 手动验证。

**Goal:** 在 `darknight/dashboard/` 用 Vue 3 + Vite + Element Plus 从零重写管理面板，忠实还原现有功能。

**Tech Stack:** Vue 3 (`<script setup>` + TS)、Vite、Element Plus、Pinia、Vue Router(hash)、@tanstack/vue-query、vue-i18n、ofetch、zod。

## Global Constraints
- 项目必须留在 `darknight/dashboard/`；`build` 脚本 = `vite build`（接受后端追加的 `--outDir build --assetsDir statics`）。
- 路由用 `createWebHashHistory`（静态托管刷新不 404）。
- HTTP base 读 `import.meta.env.VITE_BASE_API`，默认 `/api/v1/`；dev 保留 `/api/v1` 代理。
- 无测试框架：验证 = `tsc`/`vite build` 通过 + 手动回归（登录、用户 CRUD、订阅链接、节点、主机、核心配置）。
- 命名统一：弹窗组件 `*Dialog.vue`（Element 用 `el-dialog`）。

---

## Phase A — 脚手架

### Task A.1：切换到 Vue 技术栈
- 备份旧 React `src/` 到 `src_react_backup/`（或依赖 git 历史），清空 `src/`。
- 重写 `package.json`：移除 React/Chakra 全家桶；加入 `vue`、`element-plus`、`@element-plus/icons-vue`、`pinia`、`vue-router`、`@tanstack/vue-query`、`vue-i18n`、`ofetch`、`zod`、`@vitejs/plugin-vue`、`unplugin-vue-components`、`unplugin-auto-import`。
- 重写 `vite.config.ts`：`@vitejs/plugin-vue` + Element Plus 按需导入 + `/api/v1` 代理 + `@` 别名。
- 重写 `index.html`（`#app` + `main.ts`）、`tsconfig.json`。
- 验证：`npm install` && `npm run build` 产出空壳可用。

---

## Phase B — 基础设施
- `src/shared/api/http.ts`：迁移 ofetch + token 注入（复用旧逻辑）。
- `src/shared/lib/*`：迁移 `formatByte`、`dateFormatter`、`color`、`authStorage`、`userPreferenceStorage`。
- `src/app/router.ts`：hash 路由 + 守卫（`GET /admin` 校验，失败跳 `/login`）。
- `src/app/i18n.ts` + `src/locales/*`：迁移中英文案。
- `src/main.ts`：挂载 pinia/router/i18n/ElementPlus/VueQuery。
- `src/App.vue`、`src/layouts/DashboardLayout.vue`（侧栏菜单：用户/节点/主机/设置 + 顶栏：主题切换/语言/管理员）。
- `src/components/ThemeToggle.vue`、`LanguageSwitch.vue`、`StatusTag.vue`。
- `src/pages/LoginPage.vue`：`/admin/token` 登录。
- 验证：登录 → 进入布局 → 守卫生效。

---

## Phase C — Users 模块
- `features/users/types.ts`（User/UserCreate/Status/Proxies…，迁移旧类型）。
- `features/users/api/*`：vue-query —— `useUsers`(GET /users)、`useCreateUser`、`useUpdateUser`、`useDeleteUser`、`useResetUserUsage`、`useResetAllUsage`、`useRevokeSub`、`useUserUsage`、`useInbounds`。
- `features/users/store.ts`：筛选/分页/弹窗开关/选中用户。
- `features/users/components/UsersTable.vue`（`el-table` + 分页 + 状态标签 + 用量进度 + 在线 + 行操作）。
- `features/users/components/UserFilters.vue`（搜索/状态/排序）。
- `features/users/components/UserForm/*`（用户名、proxies、inbounds、限额+重置策略、expire/on_hold、备注）。
- `features/users/dialogs/*`：`UserDialog`、`DeleteUserDialog`、`QRCodeDialog`、`ResetUserUsageDialog`、`ResetAllUsageDialog`、`RevokeSubscriptionDialog`。
- `pages/UsersPage.vue` 组合以上。
- 验证：增删改查、筛选分页、二维码、复制订阅、重置用量、撤销订阅全部可用。

---

## Phase D — Nodes 模块
- `features/nodes/{types,api,store}`：GET/POST/PUT/DELETE `/node(s)`、reconnect、`/nodes/usage`。
- `features/nodes/components/NodesTable.vue` + `NodeForm` + `dialogs/{NodeDialog,DeleteNodeDialog}` + `NodesUsage.vue`（图表）。
- `pages/NodesPage.vue`。
- 验证：节点增删改、重连、用量图。

---

## Phase E — Hosts 模块
- `features/hosts/{types,api,store}`：GET/PUT `/hosts`。
- `features/hosts/components/HostForm/*`：按区块拆（基础 remark/address/port、TLS/security/sni/alpn/fingerprint、fragment、noise、mux、sockopt、allowinsecure/path），每块 < 300 行。
- `features/hosts/dialogs/HostsDialog.vue`。
- `pages/HostsPage.vue`。
- 逐字段对照旧 `HostsDialog/index.tsx` 还原。
- 验证：读取/编辑各区块/保存生效。

---

## Phase F — Settings & Stats
- `features/settings/*`：`GET /core`、`GET/PUT /core/config`、`POST /core/restart`、日志 WebSocket；JSON 编辑器。
- `components/Statistics.vue`：`GET /system` 概览卡片。
- `pages/SettingsPage.vue`。
- 验证：查看版本/状态、编辑并保存 xray 配置、重启、日志、统计。

---

## Phase G — 收尾
- 删除旧 React 备份、残留资源；`tsc`/`vite build` 通过；ESLint(vue) 通过。
- 全流程人工回归。
- 更新根 README/构建说明（如需）。

---

## Self-Review
- 后端托管约束（目录、build 脚本、hash 路由、VITE_BASE_API）在 Global Constraints 固化。✅
- 全部 API 端点分配到 C/D/E/F 模块。✅
- 巨型文件通过 Element 内置组件 + 区块拆分解决。✅
- 每阶段可构建、可回归。✅
