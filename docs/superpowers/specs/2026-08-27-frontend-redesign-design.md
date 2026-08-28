# 前端改版设计：设计系统地基 + 结算流程

日期：2026-08-27
状态：已确认，待实现（本会话复确认：两栏结算页 + 整条购买链路 + 设计系统一起做）

## 背景

现有前端是 Vue 3 + Element Plus 的单一 SPA（`darknight/dashboard`，约 7500 行、40 个 `.vue`），
视觉上停留在 Element Plus 默认观感：卡片平铺、缺少层次、主色 `#20a397` 在 16 个文件里写死了 112 处。
用户希望整体观感达到现代 SaaS 结算页的水准。视觉锚点是 Paddle 式居中两栏结算面板
（左订单概览、右填卡付款），不是支付方式选择弹窗。

已确认的产品决策：

- 范围：门户、官网、认证、admin 四个区全部改版；本 spec 只做地基 + 购买三页。
- 主色：从青绿 `#20a397` 换成紫蓝色系。
- 主题：亮色与暗色都要支持。
- 组件方案：彻底移除 Element Plus，改用 shadcn-vue（Reka UI + Tailwind CSS v4）。
- 图标：改用 `lucide-vue-next`。
- 日期选择器：用原生 `input[type="datetime-local"]` 套自有样式，不引日历库。
- 结算页：脱离侧边栏，做成全屏灰底 + 居中独立面板。
- 订单概览：不放产品图标、不放税费行，只保留小计 / 折扣 / 总计。
- 优惠码只在配置页填写；结算页只展示已锁定的折扣，不提供「添加折扣」。

## 整体拆解

改版拆成 5 个 spec，每个独立设计、实现、验收。Element Plus 到 spec 5 才卸载，
中间每一步产物都可构建、可发布。

| # | 内容 | 涉及文件 |
|---|---|---|
| 1 | **地基 + 结算流程**（本文档） | 构建配置、令牌层、首批 UI 组件、`Buy/index.vue`、`Buy/Configure.vue`、`Orders/Detail.vue`、`Buy/components/OrderSummary.vue`、`Buy/components/PayPalCardForm.vue` |
| 2 | 门户外壳与其余门户页 | `layout/UserLayout`、`portal/Dashboard`、`portal/Orders/index.vue`、`portal/Docs`、`portal/Placeholder` |
| 3 | 官网 + 认证 | `layout/SiteLayout`、`site/Home`、`auth/Login`、`portal/Register`、`Register/components/SlideCaptchaDialog` |
| 4 | admin 后台 | `layout/components/*`、`admin/Host`、`admin/Node`、`admin/User`、`admin/Setting` |
| 5 | 摘除 Element Plus | 卸载依赖、移除 `ElementPlusResolver`、移除 `el-config-provider`、清理 `build/vite/optimize.ts`、lint 规则 |

本文档只覆盖 spec 1。

## 一、地基

### 1.1 依赖变更

新增运行时依赖：

- `tailwindcss`、`@tailwindcss/vite` —— Tailwind v4，通过 Vite 插件接入，不需要 `tailwind.config.js`。
- `reka-ui` —— shadcn-vue 的无头组件基座。
- `lucide-vue-next` —— 图标。
- `class-variance-authority`、`clsx`、`tailwind-merge` —— shadcn-vue 组件的样式组合工具。
- `tw-animate-css` —— shadcn-vue 的动画工具类。
- `vue-sonner` —— 替代 `ElMessage` 的 toast。

保留（spec 5 才移除）：`element-plus`、`@element-plus/icons-vue`。

### 1.2 构建配置

`vite.config.ts` 的 `plugins` 由 `build/vite/index.ts` 的 `createVitePlugins()` 提供，
在其中加入 `tailwindcss()`。

`unplugin-vue-components` 当前配置为 `globs: ['src/components/**/*.vue']`，
会把 `src/components/ui/**` 下的 shadcn 组件也自动注册为全局组件，
与 shadcn 自身的 `index.ts` 具名导出冲突（同名组件两种注册路径）。
必须把 `ui/**` 从 glob 中排除，shadcn 组件一律显式 import。

`ElementPlusResolver` 保持不变，spec 1 期间新旧组件并存。

### 1.3 目录结构

```
src/
  assets/css/globals.css     # 新增：@import "tailwindcss" + 令牌定义
  lib/utils.ts               # 新增：cn() helper
  components/ui/**           # 新增：shadcn-vue 组件源码
  styles/index.scss          # 保留，逐步瘦身
```

`components.json` 置于 `darknight/dashboard/` 根目录，配置为：
`style: new-york`、`tailwind.config: ""`（v4 留空）、`tailwind.css: src/assets/css/globals.css`、
`tailwind.baseColor: neutral`、`tailwind.cssVariables: true`、`iconLibrary: lucide`、`rtl: true`。

`main.ts` 中 `globals.css` 必须在 `element-plus/dist/index.css` 之后引入，
以便 Tailwind 的工具类优先级高于 Element Plus 的基础样式。

### 1.4 设计令牌

`globals.css` 中定义 `:root`（亮色）与 `.dark`（暗色）两套 OKLCH 变量，基色用 neutral。

主色取靛蓝：亮色 `--primary: oklch(0.585 0.233 277.1)`（约 `#6366F1`），
暗色下提亮为 `oklch(0.66 0.19 277.1)` 以保证在深色背景上的对比度。
`--primary-foreground` 两套均为接近纯白的浅色。

现有 `src/store/modules/theme.ts` 已经在 `document.documentElement` 上切换 `dark` class，
与 shadcn-vue 的暗色约定完全一致，主题切换逻辑不需要任何改动。

`main.ts` 已引入 `element-plus/theme-chalk/dark/css-vars.css`，
Element Plus 的暗色变量与新令牌可以共存，互不覆盖（前缀分别是 `--el-` 和无前缀语义名）。

被替换掉的写死颜色（`#20a397`、`#1b8c82`、`#1b8f84`、`#303133`、`#606266`、`#909399`、`#dcdfe6`、`#e4e7ed`、`#f5f7fa`、`#eef2f6` 等）
在本 spec 涉及的 5 个文件内全部清除，改用令牌。其余文件在后续 spec 处理。

### 1.5 首批 UI 组件

spec 1 需要引入的 shadcn-vue 组件：
`button`、`card`、`input`、`label`、`badge`、`separator`、`alert`、`skeleton`、`sonner`、`alert-dialog`。

### 1.6 命令式 API 的替代

这三个是跨页面共用的基础设施，必须在 spec 1 建好，否则后续每个 spec 都会被阻塞：

| 现状 | 替代方案 | 现有用量 |
|---|---|---|
| `ElMessage.success/error` | `vue-sonner` 的 `toast`，在 `App.vue` 挂 `<Toaster>` | 17 个文件 |
| `ElMessageBox.confirm` | shadcn 的 `AlertDialog`，封装成 `useConfirm()` 组合式函数返回 Promise，保持调用点写法不变 | `Orders/Detail.vue`、admin 若干 |
| `v-loading` 指令 | 自写 `<LoadingOverlay>` 组件（绝对定位半透明遮罩 + 旋转图标） | `Orders/Detail.vue`、`PayPalCardForm.vue`、admin 若干 |

`useConfirm()` 返回 Promise 而非回调，是为了让现有 `try { await ElMessageBox.confirm(...) } catch { return }`
的调用模式可以原样保留，减少迁移时的逻辑改动。

规格 1 只迁移购买/结算相关调用点（`Buy/*`、`Orders/Detail.vue`）。
`App.vue` 挂上 `<Toaster>`，`useConfirm()` 与 `<LoadingOverlay>` 作为基础设施就位；
admin 与其它门户页的 `ElMessage` / `ElMessageBox` / `v-loading` 留到对应 spec 再换。

### 1.7 RTL

项目支持波斯语，`App.vue` 根据 locale 设置 `dir="rtl"`。
`components.json` 开启 `rtl: true`；所有自写样式使用逻辑属性
（`ms-`/`me-`/`ps-`/`pe-`/`start-`/`end-`/`text-start`/`text-end`），
禁止使用 `ml-`/`mr-`/`pl-`/`pr-`/`left-`/`right-`/`text-left`/`text-right`。

### 1.8 Tailwind preflight 与 Element Plus 的冲突

Tailwind v4 的 preflight 会重置按钮、表单、标题、列表等元素的基础样式，
而 spec 1 到 spec 4 期间 Element Plus 组件仍在页面上运行。

处理策略分两级，按顺序尝试：

1. 先按默认全局 preflight 接入，在验证阶段逐个检查 admin 的表格、表单、弹窗、分页。
   出现的零星破坏用 `@layer base` 针对 `.el-*` 选择器补回被重置的属性。
2. 若第 1 级需要补的选择器超过 10 条，改为不引入全局 preflight
   （`@import "tailwindcss"` 拆成 `@import "tailwindcss/theme"` 与 `@import "tailwindcss/utilities"`，
   跳过 `preflight`），另在 `globals.css` 里自写一份仅作用于新页面根元素的重置。

这是共存期唯一的已知真实冲突点，必须在 spec 1 验证清单里逐项过。

## 二、结算流程

### 2.1 路由调整

`/portal/orders/:orderId` 当前是 `UserLayout` 的子路由。
改为顶层独立路由（不套 `UserLayout`），以实现全屏结算面板。
鉴权守卫 `authType: 'user'` 保持不变。

`/portal/buy` 和 `/portal/buy/:planId` 仍留在 `UserLayout` 内，本 spec 只换视觉不动路由。

### 2.2 结算页布局（`Orders/Detail.vue`）

全屏浅灰底（`bg-muted`），居中一个最大宽度约 900px、圆角约 16px、
带柔和投影的面板（`bg-card`），内部左右两栏，窄屏下纵向堆叠。

**左栏**（固定约 380px，浅色背景区分）：

1. 标题「订单概览」
2. 总价，大号加粗，主色
3. 套餐名 + 周期描述（由 i18n 根据 `plan_id` 与 `cycle_id` 生成）
4. 分隔线
5. 小计 / 折扣（有折扣时才显示）/ 总计 三行

不含产品图标，不含税费行，不含「添加折扣」入口。优惠码已在配置页校验并随订单锁定。

**右栏**（自适应宽度）：

1. 两段式步骤指示：「订单信息 › 付款」，当前步为「付款」
2. PayPal 卡片字段（卡号、持卡人、有效期、安全码）
3. 满宽主按钮「支付 US$xx.xx」
4. 底部一行小字：订单号 · 创建时间
5. 「关闭订单」降级为低调的文字按钮

原有的「产品信息」「订单信息」两张独立卡片取消，信息按上述位置合并。

**支付成功态**：不跳页，面板原地切换为成功态（对勾图标 + 标题 + 「去仪表盘」「看文档」两个按钮）。

**支付失败态**：右栏内联错误提示 + 「重试」按钮，保持现有
「失败后重新 prepare-payment 换新 PayPal 订单」的逻辑不变。

### 2.3 PayPal CardFields 的样式与主题（关键风险点）

PayPal CardFields 渲染在 iframe 内，Tailwind 的 class 无法穿透，
输入框的字体、字号、颜色、聚焦态只能通过 `paypal.CardFields({ style: {...} })`
在初始化时传入，且传入的必须是具体色值，不能是 CSS 变量引用。

由此产生两个必须处理的问题：

1. **色值来源**：初始化前用 `getComputedStyle(document.documentElement)` 读取当前主题的令牌值，
   转换成 iframe 可接受的格式后传给 `style`。
2. **主题切换**：切换亮暗时 iframe 内的样式不会跟随变化，必须销毁并重建 fields。
   `PayPalCardForm.vue` 已有 `teardownFields()` 与「按 `paypalOrderId` 变化重建」的机制，
   增加一个对 `useThemeStore().mode` 的 watch 复用同一套重建流程即可。
   重建会清空用户已填的卡号，因此仅在 `paying === false` 时执行；
   若正在支付中则跳过重建，等本次支付结束。

现有的 `settled` / `errorNotified` / `destroyed` 三个状态标志用于防止扣款成功后
SDK 回调重复报错，这套逻辑与视觉改版无关，原样保留。

### 2.4 套餐页与配置页

`Buy/index.vue`：筛选按钮改为 shadcn 风格的分段控件；套餐卡改用 `Card`，
增大圆角与内边距，价格数字加大，特性列表的对勾图标换成 lucide 的 `Check`，
主按钮换成 `Button`。三列网格与窄屏单列的响应式行为保持不变。
不做周期折扣徽章：后端 `/plans` 没有对比价或节省比例字段，不编造百分比。

`Buy/Configure.vue`：周期选项改为带选中态边框与主色环的可点击卡片；
`OrderSummary.vue` 与结算页左栏共用同一套小计 / 折扣 / 总计的展示结构。

`OrderSummary.vue` 现有的 props 契约（`amount`/`discount` 由订单页传入锁定值，
配置页则取当前价目表）与优惠码校验逻辑不变，只换渲染。

### 2.5 文案

新增的 i18n key（步骤指示、订单概览标题、周期描述等）需要在
`zh.json`、`en.json`、`ru.json`、`fa.json` 四个文件同步添加。
被移除的卡片标题对应的 key 若其他页面未引用则一并删除。
`portal.buy.productInfo` 仍被订单列表页使用，必须保留。

## 三、不做的事

- 不改后端。不给 plan 加 icon/description 字段，不给订单加 tax 字段。
- 不新增支付方式。参考图里的 Apple Pay / Google Pay / 加密货币 / 支付宝、
  以及 Paddle 式的 PayPal 钱包快捷按钮，都不在范围内；仍只有 PayPal 银行卡。
- 不改购买流程的步数。仍是「选套餐 → 配置 → 支付」三页，不合并成弹窗。
- 不做套餐卡折扣徽章（没有对比价数据）。
- 不动 admin 的任何页面结构，spec 1 对 admin 的唯一影响是令牌换色与 preflight 兼容性。

## 四、验证

项目未配置测试框架（`package.json` 中无 vitest 或其他 runner），
本 spec 不引入测试框架，采用自动检查 + 手动清单：

**自动检查**（全部必须通过）：

- `npm run ts:check`
- `npm run lint`
- `npm run build`

**手动清单**：

1. 结算全链路：选套餐 → 配置周期 → 应用优惠码 → 下单 → 填卡 → 支付成功。
2. 支付失败后重试，确认换发了新的 PayPal 订单且能再次提交。
3. 亮色 / 暗色各走一遍，重点确认 PayPal iframe 内的文字在暗色下可读。
4. 支付过程中切换主题，确认不会清空已填卡号。
5. 中 / 英 / 俄 / 波斯四种语言，波斯语确认 RTL 下布局不错位。
6. 窄屏（≤960px）下结算面板正确堆叠为单列。
7. admin 四个页面（Host、Node、User、Setting）的表格、表单、弹窗、分页
   在接入 Tailwind preflight 后无视觉破坏。
