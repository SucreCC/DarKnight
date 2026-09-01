# 前端改版设计：官网 + Admin + 卸载 Element Plus

日期：2026-09-01  
状态：已确认，待写实现计划  
前置：
- `2026-08-27-frontend-redesign-design.md`（地基 + 购买链路）
- `2026-08-31-portal-shell-and-pages-design.md`（门户壳 + 认证 + 门户主页，已落地）

## 背景

门户壳、登录/注册、仪表盘、文档、订单列表与购买流程已统一为 Tailwind + shadcn、紫主色白卡片风格。  
仍割裂的部分：官网（`SiteLayout` + Home，Home 仍硬编码 `#20a397`）、门户占位页、整块 Admin（壳 + 四业务页）、以及全局 Element Plus 依赖（含 `LanguageSwitch` / `ThemeToggle`）。

本 spec 覆盖剩余全站统一，并在末尾卸载 Element Plus。

## 已确认决策

| 项 | 决策 |
|---|---|
| 范围 | 官网 + 占位页 + Admin 壳与全部业务页 + 共享组件 + 卸载 Element |
| 技术路线 | 全部逐步换成 Tailwind + shadcn（与门户一致），不做「只换 Element 主题」 |
| 落地方式 | 按区推进：官网 → 占位 → 共享组件 → Admin 壳 → Setting/Node/Host → User → 扫残留并卸载 |
| Element | 本批一并卸载；`LanguageSwitch` / `ThemeToggle` 一并迁移 |
| 本批不做 | 官网新营销内容、占位页真实功能、新 Admin 功能、后端 API 变更 |

## 一、官网 + 占位

### SiteLayout（`layout/SiteLayout/index.vue`）

- 白顶栏 + `border-border`；品牌 `text-foreground`
- 登录：`Button variant="outline"`；注册：primary `Button`
- 主区 `bg-muted/40`；页脚 muted
- 清除硬编码灰/白 hex

### Home（`views/site/Home/index.vue`）

- Hero：去掉青绿渐变；改为白/浅卡或 `bg-primary` + `text-primary-foreground`
- CTA：shadcn Button；特性三列白卡 + lucide（如 `Lock` / `Cable` / `FileText`）
- 清除全部 `#20a397`

### Placeholder（`views/portal/Placeholder/index.vue`）

- 白卡 `rounded-xl border border-border bg-card` + 居中「即将推出」文案
- 不再使用 `el-card` / `el-empty`

## 二、共享组件

### LanguageSwitch

- 用 DropdownMenu 或原生 `<select>` 套 token 样式替换 `el-select`
- 行为不变：`SUPPORTED_LOCALES` + `setLocale`

### ThemeToggle

- `Button variant="ghost" size="icon"` + lucide `Moon` / `Sun`
- 逻辑仍走 `useThemeStore`

## 三、Admin 壳

信息架构不变：可折叠侧栏 + 顶栏 + 可选 TagsView + 主内容 + 设置面板。

| 文件 | 目标 |
|------|------|
| `layout/index.vue` | 侧栏 `bg-card border-e`；主区 `bg-muted/40`；去掉 `--el-*` |
| `layout/components/Menu` | 原生 button + lucide；当前项 `bg-primary/10 text-primary`；折叠只显示图标 |
| `layout/components/ToolHeader` | 白顶栏；ghost icon Button；用户菜单用 DropdownMenu |
| `layout/components/Breadcrumb` | 轻量文字分隔，不用 `el-breadcrumb` |
| `layout/components/TagsView` | 圆角 chip + 关闭；激活态 primary；点击/关闭行为不变 |
| `layout/components/Setting` | Tailwind 侧滑面板（或等价）；开关不用 `el-drawer`/`el-switch` |

按需补 shadcn：Select / Switch / Dialog / Sheet —— 仅当原生成本更高时再加。

路由 `meta.icon` 从 Element 名改为 lucide 名（与门户批处理方式一致）。

## 四、Admin 业务页

共用替换：

- 表格 → 语义化 `<table>` + Skeleton；状态 Badge
- 控件 → Button / Input / Label
- 确认 → AlertDialog；提示 → `toast`（vue-sonner）
- 图标 → lucide；校验 → 页面内轻量函数
- 分页 → 简单上一页/下一页 + 页码（不引重型 table 库）

| 页面 | 路径要点 | 顺序 |
|------|----------|------|
| Setting | 工具栏 + JSON textarea + 日志白卡；保存/重启 Button；toast | 先 |
| Node | 列表表 + 新建/编辑对话框 + 删除确认 | 中 |
| Host | 按 tag 分组表单（`<details>` 或自写折叠）；布尔 switch；保存 toast | 中–后 |
| User | Filters + Statistics + 表格 + UserDialog / QRCodeDialog；删除/重置确认 | 最后 |

业务逻辑、API、store 行为保持不变，只换 UI 层。

## 五、卸载 Element Plus

在全部页面与共享组件迁移完成后：

1. 全仓确认无 `el-*`、`element-plus`、`@element-plus/icons-vue` 引用  
2. 修改 `main.ts`：去掉 `app.use(ElementPlus)` 与相关 CSS  
3. 修改 `App.vue`：去掉 `ElConfigProvider`  
4. 清理 Vite Element resolver / optimize 配置、`package.json` 依赖、`auto-components` 等生成类型  
5. `npm run ts:check`、`npm run lint`、`npm run build` 全绿  

## 六、验收标准

- 官网无 `#20a397`；占位页为白卡风格  
- Admin 壳与四业务页主 CTA 使用 `primary`；观感与门户一致  
- 运行时无 Element Plus 依赖  
- 登录后 Admin CRUD、配置保存、日志 WebSocket、折叠侧栏、TagsView、主题/语言切换行为与现网一致  
- 已完成的门户/购买页不被破坏  

## 七、非目标

- 官网新文案/营销区块重构（仅风格）  
- 占位页（nodes/invite/profile/tickets/traffic）真实功能  
- 新 Admin 功能或 API  
- 引入重型数据表格库  

## 八、与既有改版路线的关系

对应 `2026-08-27` 路线图的 **spec 3（官网部分）+ spec 4（admin）+ spec 5（摘除 Element）**。  
认证已在 `2026-08-31` 完成，本 spec 不再重复。购买链路与门户主页不得回退其 token / 组件约定。
