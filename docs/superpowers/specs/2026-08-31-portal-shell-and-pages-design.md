# 前端改版设计：门户壳层 + 认证 + 门户主页面

日期：2026-08-31  
状态：已确认，待写实现计划  
前置：`2026-08-27-frontend-redesign-design.md`（地基 + 购买链路已落地）

## 背景

购买流程（`/portal/buy`、配置页、订单详情）已切换到 Tailwind + shadcn、紫主色与白圆角卡片风格。  
门户壳层与其余门户/认证页仍为 Element Plus + 青绿 `#20a397`，与订阅页割裂。

全站目标仍是统一到订阅页风格，并分批完成。本 spec 是第一批。

## 已确认决策

| 项 | 决策 |
|---|---|
| 全站目标 | 门户 + 官网 + 认证 + admin 全部统一；分批实施 |
| 本批范围 | 用户门户壳层 + 仪表盘 / 文档 / 订单列表 + 登录 / 注册 |
| 后续批次 | 批次 2：官网 Home + SiteLayout；批次 3：Admin 壳与各管理页 |
| 技术路线 | 逐步换成 Tailwind + shadcn（与 Buy 页一致），不做「只换 Element 主题色」 |
| 壳层策略 | 保留顶栏 + 侧栏信息架构；白底顶栏、浅侧栏、紫高亮；去掉 Element 后台感 |
| 落地方式 | 先抽共享壳与布局基建，再按页迁移 |
| 本批不做 | 官网、Admin、占位页内容重做、Buy 流程改动、业务逻辑变更、移动端侧栏抽屉 |

## 一、门户壳层 `UserLayout`

路径：`darknight/dashboard/src/layout/UserLayout/index.vue`

### 结构（不变）

- 顶栏：站点名 | 页标题 | 语言切换 + 用户菜单  
- 侧栏：按路由 `meta.group` 分组的菜单  
- 主区：`<router-view />`

### 视觉

- **顶栏**：白底、底部分割线 `border-border`；站点名 `text-foreground` 加粗；页标题 `text-muted-foreground`；去掉青绿条 `#20a397`
- **侧栏**：白/极浅底、右边框；分组标题小号 muted；菜单项圆角；hover 浅底；当前项 `bg-primary/10 text-primary`
- **主区**：`bg-muted/40`（或等价极浅灰），内边距约 24px
- **组件**：移除 `el-menu` / `el-dropdown` / `el-icon`；用户菜单用 shadcn DropdownMenu（若仓库尚无则本批补齐）；侧栏用原生 button + Tailwind
- **图标**：侧栏映射到 `lucide-vue-next`（与 Buy 一致）；路由 `meta.icon` 可改为 lucide 名或增加映射表

### 行为

- 菜单高亮、登出、拉取 `fetchPortalMe`、文档/购买/订单相关 `pageTitle` 逻辑保持不变

## 二、共享基建

- 补齐 shadcn `DropdownMenu`（若缺失），供顶栏用户菜单使用
- 可选薄封装 `PortalPage`（宽度约束 + 可选标题/间距），与 Buy 页 `max-w-*` 写法对齐；不强行重构 Buy
- 继续使用现有 `globals.css` 紫 primary token；本批不新增色板
- 门户侧图标统一倾向 lucide；不新增 Element icons 依赖面

## 三、各页目标形态

共用语言：白卡片 `rounded-xl border border-border bg-card`、标题/次要文案 token、主 CTA 为 shadcn `Button`、输入为 `Input`、错误/提示为 `Alert`；清除页面级 `#20a397` 与青绿渐变。

| 页面 | 路径 | 目标 | 主要替换 |
|------|------|------|----------|
| 登录 | `views/auth/Login/index.vue` | 浅灰底 + 居中白卡；站点名 + 表单 + 去注册 | `el-card/form/input/button` → Card / Input / Label / Button |
| 注册 | `views/portal/Register/index.vue` | 同登录布局；验证码行；滑块验证码可暂留功能、外层样式对齐 | 同上；`ElMessage` → sonner |
| 仪表盘 | `views/portal/Dashboard/index.vue` | 公告白卡 + Badge（不再深蓝青绿渐变）；订阅卡 + 快捷入口双列白卡；空订阅虚线 CTA | `el-card/tag/input/button` → Card / Badge / Input / Button；lucide |
| 文档列表 | `views/portal/Docs/index.vue` | 白卡；搜索；分组标题；文章行 hover 浅底 | Input + 列表按钮；Search lucide |
| 文档详情 | `views/portal/Docs/Detail.vue` | 白卡正文；返回/操作为 primary/outline Button | Element 按钮/区块 → Button + Card |
| 订单列表 | `views/portal/Orders/index.vue` | 白卡包表；状态 Badge；待支付 Button；Skeleton 加载 | `el-table` → 语义化 table 或网格行；`el-alert` → Alert |

### 实施顺序

1. `UserLayout` + DropdownMenu（如需）  
2. 登录 / 注册  
3. 仪表盘  
4. 文档列表 + 详情  
5. 订单列表  

## 四、验收标准

- 门户壳无青绿顶栏；当前菜单紫高亮
- 登录、注册、仪表盘、文档、订单列表无页面级 `#20a397`；主 CTA 使用 `primary`
- 桌面布局可读；窄屏仪表盘双列变单列；侧栏桌面行为与现网一致（本批不做移动抽屉）
- 登录跳转、注册验证码/滑块、复制订阅链接、打开订单详情等行为不变
- Buy / 订单详情页观感与功能不被破坏

## 五、非目标（本批）

- `SiteLayout` / `site/Home`
- Admin 布局与 `admin/*` 页面
- 占位页（nodes / invite / profile / tickets / traffic）内容重做
- 卸载 Element Plus（全站摘除仍属后续批次）
- 新业务功能、API 变更、文案产品改写（除非为组件替换所必需）

## 六、与既有改版路线的关系

`2026-08-27` 文档将改版拆为 5 段。本 spec 覆盖其中 **门户外壳与主门户页 + 认证**，对应原路线的 spec 2 主体与 spec 3 的认证部分；官网与 admin 仍留给后续批次。购买链路（原 spec 1）已完成，本批不得回退其设计 token 与组件约定。
