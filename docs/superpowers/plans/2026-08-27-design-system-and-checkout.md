# 设计系统地基 + 结算流程改版 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 `darknight/dashboard` 中接入 Tailwind v4 + shadcn-vue 设计系统，并用它重写购买与结算流程，使结算页成为居中的两栏独立面板。

**Architecture:** Tailwind v4 通过 `@tailwindcss/vite` 插件接入，设计令牌以 OKLCH CSS 变量形式定义在 `src/assets/css/globals.css` 的 `:root` 与 `.dark` 下，由现有 `theme.ts` 切换。shadcn-vue 组件源码落在 `src/components/ui/**`，显式 import。Element Plus 在本计划期间继续保留并与新体系共存，直到后续 spec 5 才卸载。

**Tech Stack:** Vue 3.5、Vite 6、TypeScript 5.7、Tailwind CSS v4、shadcn-vue（Reka UI）、lucide-vue-next、vue-sonner、vue-i18n 10、@tanstack/vue-query 5、@paypal/paypal-js 11

## Global Constraints

- 所有命令在 `e:\kai\DarKnight\darknight\dashboard` 目录下执行，包管理器用 `npm`。
- 主色亮色 `oklch(0.585 0.233 277.1)`（约 `#6366F1`），暗色 `oklch(0.66 0.19 277.1)`；两套 `--primary-foreground` 均为 `oklch(0.985 0 0)`。
- 基色用 neutral，shadcn 风格用 `new-york`，`cssVariables: true`，`iconLibrary: lucide`，`rtl: true`。
- 本计划触及的文件内不得残留写死颜色（`#20a397`、`#1b8c82`、`#1b8f84`、`#303133`、`#606266`、`#909399`、`#dcdfe6`、`#e4e7ed`、`#f5f7fa`、`#eef2f6`），一律改用令牌；`src/assets/css/globals.css` 中为 PayPal iframe 定义的专用 hex 变量是唯一例外。
- 所有间距、定位类一律用逻辑属性（`ms-`/`me-`/`ps-`/`pe-`/`start-`/`end-`/`text-start`/`text-end`），禁止 `ml-`/`mr-`/`pl-`/`pr-`/`left-`/`right-`/`text-left`/`text-right`。项目支持波斯语 RTL。
- 不改后端，不新增支付方式，不改购买流程的页面数量。
- 不做套餐卡折扣徽章（后端没有对比价）。结算页不提供「添加折扣」，优惠码只在配置页填写。
- spec 1 只把购买/结算相关调用点从 `ElMessage` 换成 toast；admin 与其它门户页留到对应 spec。
- `portal.buy.productInfo` 仍被订单列表页使用，禁止删除。
- 不引入测试框架（`package.json` 中没有 runner，spec 明确不加）。每个任务的验收 = `npm run ts:check` + `npm run lint` + `npm run build` 全过，再加该任务自己的手动检查项。
- i18n 语言文件是**扁平点号键**（`"portal.buy.orderTotal": "订单总额"`），不是嵌套对象。新增 key 必须同时写入 `zh.json`、`en.json`、`ru.json`、`fa.json` 四个文件。
- 每个任务结束时提交一次。提交信息用英文，格式 `feat(dashboard): ...` / `refactor(dashboard): ...` / `chore(dashboard): ...`。

---

### Task 1: 接入 Tailwind v4 与设计令牌

**Files:**
- Modify: `darknight/dashboard/package.json`
- Modify: `darknight/dashboard/build/vite/index.ts`
- Modify: `darknight/dashboard/src/main.ts:1-7`
- Modify: `darknight/dashboard/stylelint.config.js:31-36`
- Modify: `darknight/dashboard/eslint.config.mjs:8-16`
- Create: `darknight/dashboard/src/assets/css/globals.css`
- Create: `darknight/dashboard/src/lib/utils.ts`
- Create: `darknight/dashboard/components.json`

**Interfaces:**
- Consumes: 无（首个任务）
- Produces:
  - CSS 令牌：`--background` `--foreground` `--card` `--card-foreground` `--popover` `--popover-foreground` `--primary` `--primary-foreground` `--secondary` `--secondary-foreground` `--muted` `--muted-foreground` `--accent` `--accent-foreground` `--destructive` `--destructive-foreground` `--border` `--input` `--ring` `--radius`
  - PayPal iframe 专用 hex 令牌：`--paypal-field-color` `--paypal-field-placeholder` `--paypal-field-focus` `--paypal-field-invalid`
  - Tailwind 工具类：`bg-background` `text-foreground` `bg-card` `bg-muted` `text-muted-foreground` `bg-primary` `text-primary` `border-border` `rounded-lg` 等
  - `cn(...inputs: ClassValue[]): string`，从 `@/lib/utils` 导出

- [ ] **Step 1: 安装依赖**

```bash
cd darknight/dashboard
npm i tailwindcss @tailwindcss/vite reka-ui lucide-vue-next class-variance-authority clsx tailwind-merge tw-animate-css vue-sonner
```

- [ ] **Step 2: 创建 `src/lib/utils.ts`**

```ts
import type { ClassValue } from 'clsx'
import { clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs))
}
```

- [ ] **Step 3: 创建 `src/assets/css/globals.css`**

主色是靛蓝 `oklch(0.585 0.233 277.1)`。`--paypal-*` 四个变量必须写成十六进制而非 oklch —— 它们会被 JS 读出来传进 PayPal 的 iframe，iframe 内的 CSS 解析不保证支持 oklch。

```css
@import 'tailwindcss';
@import 'tw-animate-css';

@custom-variant dark (&:is(.dark *));

:root {
  --radius: 0.75rem;
  --background: oklch(1 0 0);
  --foreground: oklch(0.145 0 0);
  --card: oklch(1 0 0);
  --card-foreground: oklch(0.145 0 0);
  --popover: oklch(1 0 0);
  --popover-foreground: oklch(0.145 0 0);
  --primary: oklch(0.585 0.233 277.1);
  --primary-foreground: oklch(0.985 0 0);
  --secondary: oklch(0.97 0 0);
  --secondary-foreground: oklch(0.205 0 0);
  --muted: oklch(0.97 0 0);
  --muted-foreground: oklch(0.556 0 0);
  --accent: oklch(0.97 0 0);
  --accent-foreground: oklch(0.205 0 0);
  --destructive: oklch(0.577 0.245 27.325);
  --destructive-foreground: oklch(0.985 0 0);
  --border: oklch(0.922 0 0);
  --input: oklch(0.922 0 0);
  --ring: oklch(0.585 0.233 277.1);
  --paypal-field-color: #18181b;
  --paypal-field-placeholder: #a1a1aa;
  --paypal-field-focus: #6366f1;
  --paypal-field-invalid: #ef4444;
}

.dark {
  --background: oklch(0.145 0 0);
  --foreground: oklch(0.985 0 0);
  --card: oklch(0.205 0 0);
  --card-foreground: oklch(0.985 0 0);
  --popover: oklch(0.205 0 0);
  --popover-foreground: oklch(0.985 0 0);
  --primary: oklch(0.66 0.19 277.1);
  --primary-foreground: oklch(0.985 0 0);
  --secondary: oklch(0.269 0 0);
  --secondary-foreground: oklch(0.985 0 0);
  --muted: oklch(0.269 0 0);
  --muted-foreground: oklch(0.708 0 0);
  --accent: oklch(0.269 0 0);
  --accent-foreground: oklch(0.985 0 0);
  --destructive: oklch(0.704 0.191 22.216);
  --destructive-foreground: oklch(0.985 0 0);
  --border: oklch(1 0 0 / 10%);
  --input: oklch(1 0 0 / 15%);
  --ring: oklch(0.66 0.19 277.1);
  --paypal-field-color: #fafafa;
  --paypal-field-placeholder: #71717a;
  --paypal-field-focus: #818cf8;
  --paypal-field-invalid: #f87171;
}

@theme inline {
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --color-card: var(--card);
  --color-card-foreground: var(--card-foreground);
  --color-popover: var(--popover);
  --color-popover-foreground: var(--popover-foreground);
  --color-primary: var(--primary);
  --color-primary-foreground: var(--primary-foreground);
  --color-secondary: var(--secondary);
  --color-secondary-foreground: var(--secondary-foreground);
  --color-muted: var(--muted);
  --color-muted-foreground: var(--muted-foreground);
  --color-accent: var(--accent);
  --color-accent-foreground: var(--accent-foreground);
  --color-destructive: var(--destructive);
  --color-destructive-foreground: var(--destructive-foreground);
  --color-border: var(--border);
  --color-input: var(--input);
  --color-ring: var(--ring);
  --radius-sm: calc(var(--radius) - 4px);
  --radius-md: calc(var(--radius) - 2px);
  --radius-lg: var(--radius);
  --radius-xl: calc(var(--radius) + 4px);
}
```

- [ ] **Step 4: 创建 `components.json`**

`tailwind.config` 在 v4 下必须留空字符串。

```json
{
  "$schema": "https://shadcn-vue.com/schema.json",
  "style": "new-york",
  "typescript": true,
  "tailwind": {
    "config": "",
    "css": "src/assets/css/globals.css",
    "baseColor": "neutral",
    "cssVariables": true,
    "prefix": ""
  },
  "aliases": {
    "components": "@/components",
    "composables": "@/composables",
    "utils": "@/lib/utils",
    "ui": "@/components/ui",
    "lib": "@/lib"
  },
  "iconLibrary": "lucide",
  "pointer": false,
  "rtl": true
}
```

- [ ] **Step 5: 把 Tailwind 插件加进 Vite，并把 `ui/**` 从组件自动注册中排除**

`unplugin-vue-components` 现在的 `globs: ['src/components/**/*.vue']` 会把 shadcn 组件也注册成全局组件，与它们自己的 `index.ts` 具名导出冲突（同一个 `Button` 有两条注册路径），必须排除。

修改 `build/vite/index.ts`：

```ts
import Vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

export function createVitePlugins() {
  const plugins = [
    Vue(),
    tailwindcss(),
    AutoImport({
      include: [
        /\.[tj]sx?$/, // .ts, .tsx, .js, .jsx
        /\.vue$/,
        /\.vue\?vue/ // .vue
      ],
      imports: ['vue', 'vue-router', 'vue-i18n', 'pinia', '@vueuse/core'],
      resolvers: [ElementPlusResolver({ importStyle: false })],
      dts: 'types/auto-imports.d.ts',
      eslintrc: {
        enabled: true,
        filepath: './.eslintrc-auto-import.json',
        globalsPropValue: true
      }
    }),
    Components({
      dts: 'types/auto-components.d.ts',
      resolvers: [ElementPlusResolver({ importStyle: false })],
      // shadcn-vue 组件走显式 import，不能再被全局注册一次。
      globs: ['src/components/**/*.vue', '!src/components/ui/**']
    })
  ]

  return plugins.filter(Boolean)
}
```

- [ ] **Step 6: 在 `src/main.ts` 引入 `globals.css`**

必须排在 `element-plus/dist/index.css` 之后，让 Tailwind 工具类优先级高于 Element Plus 的基础样式。把 `src/main.ts` 第 4-7 行改成：

```ts
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/dark/css-vars.css'
import '@/assets/css/globals.css'
import '@/styles/index.scss'
```

- [ ] **Step 7: 放行 Tailwind 的 at-rule，并让 lint 跳过 shadcn 生成的组件**

stylelint 的 `at-rule-no-unknown` 虽然已经关了，但 scss 方言下由 `scss/at-rule-no-unknown` 接管，它会拦 `@theme`、`@custom-variant`、`@apply`、`@source`、`@utility`、`@variant`、`@plugin`。

把 `stylelint.config.js` 第 32 行那条 `'at-rule-no-unknown': null,` 改成：

```js
    // scss 方言下由 scss/at-rule-no-unknown 接管。
    'at-rule-no-unknown': null,
    'scss/at-rule-no-unknown': [
      true,
      {
        ignoreAtRules: ['theme', 'custom-variant', 'apply', 'source', 'utility', 'variant', 'plugin']
      }
    ],
```

同时在 `stylelint.config.js` 的 `ignoreFiles`（第 229 行）加入 shadcn 生成的组件——这些是 vendored 源码，按上游风格生成，不该被本项目的属性排序规则约束：

```js
  ignoreFiles: ['**/*.js', '**/*.jsx', '**/*.tsx', '**/*.ts', 'src/components/ui/**'],
```

同理，在 `eslint.config.mjs` 的 `ignores` 数组（第 9-15 行）加一项 `'src/components/ui/**'`：

```js
    ignores: [
      'dist/',
      'node_modules/',
      'public/',
      'types/auto-imports.d.ts',
      'types/auto-components.d.ts',
      // shadcn-vue 生成的 vendored 组件，按上游风格维护。
      'src/components/ui/**'
    ]
```

- [ ] **Step 8: 用一次性探针验证 Tailwind 真的生效**

临时把 `src/App.vue` 的模板改成：

```vue
<template>
  <el-config-provider :locale="undefined">
    <div :dir="rtl" class="dk-app">
      <div class="fixed bottom-2 end-2 z-50 rounded-lg bg-primary px-3 py-1 text-primary-foreground">
        tw-probe
      </div>
      <router-view />
    </div>
  </el-config-provider>
</template>
```

运行 `npm run dev`，打开 `http://localhost:3000/portal/buy`。
Expected：右下角出现一个靛蓝色圆角小标签「tw-probe」，文字为白色。
再点页面上的主题切换，确认它在暗色下变成更亮的靛蓝。
确认后把探针 `<div>` 删掉，`App.vue` 恢复原样。

- [ ] **Step 9: 检查 Tailwind preflight 有没有破坏 Element Plus**

这是新旧共存期唯一的已知真实冲突点。`npm run dev` 后逐个打开：

- `/admin/user` —— 表格、分页、筛选下拉、编辑弹窗、日期选择器
- `/admin/node` —— 表格、新增弹窗、开关
- `/admin/host` —— 折叠面板、表单、复选框
- `/admin/setting` —— 输入框、按钮、标签

Expected：按钮不塌陷成无背景的裸 `<button>`，表格边框还在，表单标签对齐正常，弹窗有背景和阴影。

若出现零星破坏，在 `src/assets/css/globals.css` 末尾追加针对性修补，例如：

```css
@layer base {
  .el-button {
    border-style: solid;
  }
}
```

若需要补的选择器超过 10 条，改走 spec 1.8 的第 2 级方案：把 `@import 'tailwindcss';` 拆成
`@import 'tailwindcss/theme.css' layer(theme);` 与 `@import 'tailwindcss/utilities.css' layer(utilities);`（跳过 preflight），
并在 `globals.css` 里自写一份只作用于 `.dk-surface` 根元素的重置。把实际采用的方案记录在提交信息里。

- [ ] **Step 10: 跑全套检查**

```bash
npm run ts:check
npm run lint
npm run build
```

Expected：三条命令全部退出码 0。

- [ ] **Step 11: 提交**

```bash
git add darknight/dashboard/package.json darknight/dashboard/package-lock.json darknight/dashboard/components.json darknight/dashboard/build/vite/index.ts darknight/dashboard/stylelint.config.js darknight/dashboard/eslint.config.mjs darknight/dashboard/src/main.ts darknight/dashboard/src/lib/utils.ts darknight/dashboard/src/assets/css/globals.css
git commit -m "feat(dashboard): add Tailwind v4 and indigo design tokens"
```

---

### Task 2: 引入首批 shadcn-vue 组件与 lucide 图标

**Files:**
- Create: `darknight/dashboard/src/components/ui/**`（由 CLI 生成）

**Interfaces:**
- Consumes: Task 1 的 `cn()`、`components.json`、`globals.css` 令牌
- Produces（全部从 `@/components/ui/<name>` 具名导出）：
  - `Button`（props：`variant?: 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link'`，`size?: 'default' | 'sm' | 'lg' | 'icon'`，`disabled?: boolean`，`as?: string`）
  - `Card` `CardHeader` `CardTitle` `CardDescription` `CardContent` `CardFooter`
  - `Input`（`v-model` 走 `defaultValue` / `modelValue`）
  - `Label`
  - `Badge`（`variant?: 'default' | 'secondary' | 'destructive' | 'outline'`）
  - `Separator`（`orientation?: 'horizontal' | 'vertical'`）
  - `Alert` `AlertTitle` `AlertDescription`（`variant?: 'default' | 'destructive'`）
  - `Skeleton`
  - `Toaster`（来自 `@/components/ui/sonner`）
  - `AlertDialog` `AlertDialogAction` `AlertDialogCancel` `AlertDialogContent` `AlertDialogDescription` `AlertDialogFooter` `AlertDialogHeader` `AlertDialogTitle`

- [ ] **Step 1: 生成组件**

```bash
cd darknight/dashboard
npx shadcn-vue@latest add button card input label badge separator alert skeleton sonner alert-dialog
```

CLI 若询问是否覆盖 `globals.css`，选**否** —— Task 1 里的令牌是定制过的，不能被默认值盖掉。

- [ ] **Step 2: 确认生成结果**

Run: `ls src/components/ui`
Expected：出现 `alert`、`alert-dialog`、`badge`、`button`、`card`、`input`、`label`、`separator`、`skeleton`、`sonner` 十个目录，每个目录内有 `index.ts`。

- [ ] **Step 3: 确认令牌没被覆盖**

Run: `rg "oklch\(0.585 0.233 277.1\)" src/assets/css/globals.css`
Expected：至少一条匹配。若无匹配说明 CLI 覆盖了文件，用 `git checkout src/assets/css/globals.css` 还原后重跑 Step 1 并选择不覆盖。

- [ ] **Step 4: 跑全套检查**

```bash
npm run ts:check
npm run lint
npm run build
```

Expected：三条命令全部退出码 0。若 `ts:check` 报 `reka-ui` 类型找不到，确认 Task 1 Step 1 的 `reka-ui` 装成功了。

- [ ] **Step 5: 提交**

```bash
git add darknight/dashboard/src/components/ui darknight/dashboard/package.json darknight/dashboard/package-lock.json
git commit -m "feat(dashboard): add first batch of shadcn-vue components"
```

---

### Task 3: 全局 toast、确认框与加载遮罩

**Files:**
- Create: `darknight/dashboard/src/composables/useConfirm.ts`
- Create: `darknight/dashboard/src/components/ConfirmDialog/index.vue`
- Create: `darknight/dashboard/src/components/LoadingOverlay/index.vue`
- Modify: `darknight/dashboard/src/App.vue`

**Interfaces:**
- Consumes: Task 2 的 `Toaster`、`AlertDialog*`、`Button`
- Produces:
  - `useConfirm(): { confirm(options: ConfirmOptions): Promise<void> }`，其中
    `interface ConfirmOptions { title: string; description: string; confirmText?: string; cancelText?: string; destructive?: boolean }`。
    用户确认时 Promise resolve，取消时 **reject**（保留调用点现有的 `try { await ... } catch { return }` 写法）。
  - `<LoadingOverlay :loading="boolean" />`，默认插槽包住内容，`loading` 为真时盖上半透明遮罩与旋转图标。
  - toast 直接用 `import { toast } from 'vue-sonner'`，调用 `toast.success(msg)` / `toast.error(msg)`。

- [ ] **Step 1: 创建 `src/components/LoadingOverlay/index.vue`**

```vue
<script setup lang="ts">
import { Loader2 } from 'lucide-vue-next'

defineProps<{ loading?: boolean }>()
</script>

<template>
  <div class="relative">
    <slot />
    <div
      v-if="loading"
      class="absolute inset-0 z-10 flex items-center justify-center rounded-[inherit] bg-background/70 backdrop-blur-[1px]"
    >
      <Loader2 class="size-6 animate-spin text-primary" />
    </div>
  </div>
</template>
```

- [ ] **Step 2: 创建 `src/components/ConfirmDialog/index.vue`**

这是 `useConfirm()` 的宿主组件，全应用只挂一个实例，状态由 composable 提供的模块级单例驱动。

```vue
<script setup lang="ts">
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle
} from '@/components/ui/alert-dialog'
import { confirmState, resolveConfirm } from '@/composables/useConfirm'
</script>

<template>
  <AlertDialog :open="confirmState.open" @update:open="(v: boolean) => !v && resolveConfirm(false)">
    <AlertDialogContent>
      <AlertDialogHeader>
        <AlertDialogTitle>{{ confirmState.options.title }}</AlertDialogTitle>
        <AlertDialogDescription>{{ confirmState.options.description }}</AlertDialogDescription>
      </AlertDialogHeader>
      <AlertDialogFooter>
        <AlertDialogCancel @click="resolveConfirm(false)">
          {{ confirmState.options.cancelText }}
        </AlertDialogCancel>
        <AlertDialogAction
          :class="confirmState.options.destructive ? 'bg-destructive text-destructive-foreground hover:bg-destructive/90' : ''"
          @click="resolveConfirm(true)"
        >
          {{ confirmState.options.confirmText }}
        </AlertDialogAction>
      </AlertDialogFooter>
    </AlertDialogContent>
  </AlertDialog>
</template>
```

- [ ] **Step 3: 创建 `src/composables/useConfirm.ts`**

```ts
import { reactive } from 'vue'
import { i18n } from '@/plugins/vueI18n'

export interface ConfirmOptions {
  title: string
  description: string
  confirmText?: string
  cancelText?: string
  destructive?: boolean
}

interface ConfirmState {
  open: boolean
  options: Required<Omit<ConfirmOptions, 'destructive'>> & { destructive: boolean }
}

export const confirmState = reactive<ConfirmState>({
  open: false,
  options: { title: '', description: '', confirmText: '', cancelText: '', destructive: false }
})

let pending: { resolve: () => void; reject: () => void } | null = null

/** 关闭对话框并结算 Promise。取消走 reject，保留调用点 try/catch 的写法。 */
export function resolveConfirm(confirmed: boolean): void {
  confirmState.open = false
  const current = pending
  pending = null
  if (!current) return
  if (confirmed) current.resolve()
  else current.reject()
}

export function useConfirm() {
  function confirm(options: ConfirmOptions): Promise<void> {
    // 同一时刻只允许一个确认框；新的请求先把旧的当作取消结算掉。
    if (pending) resolveConfirm(false)

    const t = i18n.global.t
    confirmState.options = {
      title: options.title,
      description: options.description,
      confirmText: options.confirmText ?? t('confirm'),
      cancelText: options.cancelText ?? t('cancel'),
      destructive: options.destructive ?? false
    }
    confirmState.open = true

    return new Promise<void>((resolve, reject) => {
      pending = { resolve, reject }
    })
  }

  return { confirm }
}
```

- [ ] **Step 4: 确认 `confirm` 与 `cancel` 两个 i18n key 存在**

Run: `node -e "const j=require('./src/locales/zh.json'); console.log(j.confirm, '|', j.cancel)"`
Expected：打印出两个中文词。若 `confirm` 为 `undefined`，在 `zh.json`/`en.json`/`ru.json`/`fa.json` 四个文件各加一条顶层扁平键
`"confirm"`，值分别为 `"确定"` / `"Confirm"` / `"Подтвердить"` / `"تأیید"`。

- [ ] **Step 5: 在 `App.vue` 挂载 Toaster 与 ConfirmDialog**

```vue
<script setup lang="ts">
import { computed } from 'vue'
import { ElConfigProvider } from 'element-plus'
import { useThemeStore } from '@/store/modules/theme'
import { useI18n } from 'vue-i18n'
import { Toaster } from '@/components/ui/sonner'
import ConfirmDialog from '@/components/ConfirmDialog/index.vue'

// Ensure theme store is initialized (applies dark class on load).
const theme = useThemeStore()
const { locale } = useI18n()
const rtl = computed(() => (locale.value === 'fa' ? 'rtl' : 'ltr'))
</script>

<template>
  <el-config-provider :locale="undefined">
    <div :dir="rtl" class="dk-app">
      <router-view />
      <Toaster :theme="theme.mode" position="top-center" rich-colors />
      <ConfirmDialog />
    </div>
  </el-config-provider>
</template>

<style scoped>
.dk-app {
  width: 100%;
  height: 100%;
}
</style>
```

- [ ] **Step 6: 用一次性探针验证 toast 与确认框**

临时在 `App.vue` 的 `<script setup>` 末尾加：

```ts
import { toast } from 'vue-sonner'
const { confirm } = useConfirm()
async function probe() {
  toast.success('toast probe')
  try {
    await confirm({ title: 'probe title', description: 'probe description' })
    toast.success('confirmed')
  } catch {
    toast.error('cancelled')
  }
}
```

并在模板的 `<router-view />` 后加一个按钮：

```vue
      <button class="fixed bottom-2 end-2 z-50 rounded-lg bg-primary px-3 py-1 text-primary-foreground" @click="probe">
        probe
      </button>
```

`npm run dev`，打开 `/portal/buy` 点这个按钮。
Expected：顶部中央出现绿色 toast「toast probe」，同时弹出居中的确认对话框；
点「取消」出现红色 toast「cancelled」，点「确定」出现绿色 toast「confirmed」。
切暗色重复一次，Expected：toast 与对话框都变成暗色。
确认后把 `probe` 函数、两个 import 和按钮全部删掉，`App.vue` 恢复成 Step 5 的样子。

- [ ] **Step 7: 跑全套检查**

```bash
npm run ts:check
npm run lint
npm run build
```

Expected：三条命令全部退出码 0。

- [ ] **Step 8: 提交**

```bash
git add darknight/dashboard/src/App.vue darknight/dashboard/src/composables darknight/dashboard/src/components/ConfirmDialog darknight/dashboard/src/components/LoadingOverlay darknight/dashboard/src/locales
git commit -m "feat(dashboard): add toast, confirm dialog and loading overlay primitives"
```

---

### Task 4: 新增结算流程的 i18n 文案

**Files:**
- Modify: `darknight/dashboard/src/locales/zh.json`
- Modify: `darknight/dashboard/src/locales/en.json`
- Modify: `darknight/dashboard/src/locales/ru.json`
- Modify: `darknight/dashboard/src/locales/fa.json`

**Interfaces:**
- Consumes: 无
- Produces: 新增扁平键 `portal.buy.orderOverview`、`portal.buy.subtotal`、`portal.buy.discount`、`portal.buy.grandTotal`、`portal.buy.stepOrder`、`portal.buy.stepPayment`、`portal.buy.planDescription`、`portal.buy.applyCoupon`

单独成一个任务，是因为后面三个 UI 任务都要用这批 key；先落地可以让它们并行开工，也避免同一个 JSON 被三次改动反复冲突。

- [ ] **Step 1: 往 `zh.json` 追加**

放在已有的 `"portal.buy.orderTotal"` 那一行附近，保持同类相邻。

```json
"portal.buy.orderOverview": "订单概览",
"portal.buy.subtotal": "小计",
"portal.buy.discount": "折扣",
"portal.buy.grandTotal": "总计",
"portal.buy.stepOrder": "订单信息",
"portal.buy.stepPayment": "付款",
"portal.buy.planDescription": "购买 {plan} 服务 {days} 天（一次性付款，不自动续费）",
"portal.buy.applyCoupon": "使用优惠码"
```

- [ ] **Step 2: 往 `en.json` 追加**

```json
"portal.buy.orderOverview": "Order summary",
"portal.buy.subtotal": "Subtotal",
"portal.buy.discount": "Discount",
"portal.buy.grandTotal": "Total",
"portal.buy.stepOrder": "Your details",
"portal.buy.stepPayment": "Payment",
"portal.buy.planDescription": "Purchase {plan} service for {days} days (one-time payment, no recurring charge)",
"portal.buy.applyCoupon": "Apply coupon"
```

- [ ] **Step 3: 往 `ru.json` 追加**

```json
"portal.buy.orderOverview": "Сводка заказа",
"portal.buy.subtotal": "Промежуточный итог",
"portal.buy.discount": "Скидка",
"portal.buy.grandTotal": "Итого",
"portal.buy.stepOrder": "Ваши данные",
"portal.buy.stepPayment": "Оплата",
"portal.buy.planDescription": "Покупка услуги {plan} на {days} дней (разовый платёж, без автопродления)",
"portal.buy.applyCoupon": "Применить купон"
```

- [ ] **Step 4: 往 `fa.json` 追加**

```json
"portal.buy.orderOverview": "خلاصه سفارش",
"portal.buy.subtotal": "جمع جزء",
"portal.buy.discount": "تخفیف",
"portal.buy.grandTotal": "مجموع",
"portal.buy.stepOrder": "اطلاعات شما",
"portal.buy.stepPayment": "پرداخت",
"portal.buy.planDescription": "خرید سرویس {plan} به مدت {days} روز (پرداخت یک‌باره، بدون تمدید خودکار)",
"portal.buy.applyCoupon": "اعمال کد تخفیف"
```

- [ ] **Step 5: 验证四个文件的 key 集合一致**

```bash
cd darknight/dashboard
node -e "const a=['zh','en','ru','fa'].map(l=>({l,k:Object.keys(require('./src/locales/'+l+'.json')).filter(x=>x.startsWith('portal.buy.'))})); const base=new Set(a[0].k); a.forEach(x=>{const miss=[...base].filter(k=>!x.k.includes(k)); const extra=x.k.filter(k=>!base.has(k)); console.log(x.l, 'missing:', miss, 'extra:', extra)})"
```

Expected：四行输出的 `missing` 与 `extra` 都是 `[]`。

- [ ] **Step 6: 跑检查并提交**

```bash
npm run lint
git add darknight/dashboard/src/locales
git commit -m "feat(dashboard): add i18n copy for redesigned checkout"
```

---

### Task 5: 重写 OrderSummary 为结算概览

**Files:**
- Modify: `darknight/dashboard/src/views/portal/Buy/components/OrderSummary.vue`（整文件替换）

**Interfaces:**
- Consumes: Task 2 的 `Button` `Input` `Separator`；Task 3 的 toast；Task 4 的 `portal.buy.orderOverview` `portal.buy.subtotal` `portal.buy.discount` `portal.buy.grandTotal` `portal.buy.applyCoupon`
- Produces: `OrderSummary` 组件，props 与 emits 与改造前**完全一致**，下游 `Configure.vue`、`Orders/Detail.vue` 不需要改调用方式：
  - props：`planId: string`、`cycleId: string`、`coupon?: string`、`submitLabel: string`、`loading?: boolean`、`amount?: number`、`discount?: number`、`currency?: string`、`hideSubmit?: boolean`、`readonlyCoupon?: boolean`
  - emits：`'update:coupon': [value: string]`、`submit: []`
  - 新增 props：`variant?: 'panel' | 'aside'`，默认 `'aside'`。`'panel'` 用于结算页左栏（无外框、撑满父容器），`'aside'` 用于配置页右侧（独立卡片、固定宽度）。

- [ ] **Step 1: 整文件替换 `OrderSummary.vue`**

`<script setup>` 部分只在原有基础上增加 `variant` prop 与 `toast` 替换，价格与优惠码的计算逻辑一字不改。

```vue
<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { Check } from 'lucide-vue-next'
import { toast } from 'vue-sonner'
import { previewCoupon } from '@/api/portal/orders'
import { resolvePortalApiError } from '@/utils/portalError'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Separator } from '@/components/ui/separator'
import { cn } from '@/lib/utils'
import { currencySymbol, formatPrice, getCycleLabelKey, getPlanMeta } from '../plans'
import { usePlanCatalog } from '../usePlanCatalog'

const props = withDefaults(
  defineProps<{
    planId: string
    cycleId: string
    coupon?: string
    submitLabel: string
    loading?: boolean
    /** 订单页传入下单时锁定的金额；不传则取当前价目表 */
    amount?: number
    /** 订单页传入下单时锁定的折扣 */
    discount?: number
    currency?: string
    hideSubmit?: boolean
    readonlyCoupon?: boolean
    /** panel：结算页左栏，无外框；aside：配置页右侧卡片 */
    variant?: 'panel' | 'aside'
  }>(),
  { variant: 'aside' }
)

const emit = defineEmits<{
  'update:coupon': [value: string]
  submit: []
}>()

const { t } = useI18n()
const { currency: catalogCurrency, getCycle } = usePlanCatalog()
const couponInput = ref(props.coupon ?? '')
const verifying = ref(false)
/** 已通过后端校验的折扣；仅用于展示，最终金额仍由后端下单时计算 */
const verifiedDiscount = ref(0)

const planName = computed(() => getPlanMeta(props.planId)?.name ?? props.planId)
const currencyCode = computed(() => props.currency ?? catalogCurrency.value)
const symbol = computed(() => currencySymbol(currencyCode.value))

const discount = computed(() => props.discount ?? verifiedDiscount.value)

/** 订单页显示下单时锁定的原价，配置页显示当前价目表原价 */
const listPrice = computed(() => {
  if (props.amount !== undefined) {
    return Math.round((props.amount + discount.value) * 100) / 100
  }
  return getCycle(props.planId, props.cycleId)?.price
})

const total = computed(() => {
  if (props.amount !== undefined) return props.amount
  if (listPrice.value === undefined) return undefined
  return Math.round((listPrice.value - discount.value) * 100) / 100
})

const cycleLabel = computed(() => t(getCycleLabelKey(props.cycleId)))
// 价目表还没加载时 durationDays 拿不到，此时宁可不显示描述，也不要显示「0 天」。
const durationDays = computed(() => getCycle(props.planId, props.cycleId)?.durationDays ?? 0)
const planDescription = computed(() =>
  durationDays.value > 0
    ? t('portal.buy.planDescription', { plan: planName.value, days: durationDays.value })
    : ''
)

// 换套餐或换周期后旧折扣不再适用，重新校验前先清掉。
watch([() => props.planId, () => props.cycleId], () => {
  verifiedDiscount.value = 0
  emit('update:coupon', '')
})

async function verifyCoupon() {
  const code = couponInput.value.trim()
  if (!code) {
    verifiedDiscount.value = 0
    emit('update:coupon', '')
    return
  }

  verifying.value = true
  try {
    const preview = await previewCoupon({
      plan_id: props.planId,
      cycle_id: props.cycleId,
      coupon: code
    })
    verifiedDiscount.value = preview.discount
    emit('update:coupon', preview.coupon)
    toast.success(
      t('portal.buy.couponApplied', { amount: symbol.value + formatPrice(preview.discount) })
    )
  } catch (err) {
    verifiedDiscount.value = 0
    emit('update:coupon', '')
    toast.error(resolvePortalApiError(err, t))
  } finally {
    verifying.value = false
  }
}
</script>

<template>
  <aside
    :class="
      cn(
        'flex flex-col gap-6',
        variant === 'aside'
          ? 'w-full shrink-0 rounded-xl border border-border bg-card p-6 lg:w-80'
          : 'h-full bg-muted/40 p-8'
      )
    "
  >
    <div class="space-y-4">
      <p class="text-sm font-medium text-muted-foreground">{{ t('portal.buy.orderOverview') }}</p>
      <p class="text-4xl font-bold tracking-tight text-primary">
        {{ total === undefined ? '--' : symbol + formatPrice(total) }}
      </p>
      <div class="space-y-1">
        <p class="text-base font-semibold text-foreground">{{ planName }} · {{ cycleLabel }}</p>
        <p v-if="planDescription" class="text-sm leading-relaxed text-muted-foreground">
          {{ planDescription }}
        </p>
      </div>
    </div>

    <Separator />

    <div class="space-y-3 text-sm">
      <div class="flex items-center justify-between">
        <span class="text-muted-foreground">{{ t('portal.buy.subtotal') }}</span>
        <span class="font-medium text-foreground">
          {{ listPrice === undefined ? '--' : symbol + formatPrice(listPrice) }}
        </span>
      </div>

      <div v-if="!readonlyCoupon" class="flex items-center gap-2">
        <Input
          v-model="couponInput"
          :placeholder="t('portal.buy.couponPlaceholder')"
          class="h-9"
          @keyup.enter="verifyCoupon"
        />
        <Button variant="outline" size="sm" :disabled="verifying" @click="verifyCoupon">
          {{ t('portal.buy.verifyCoupon') }}
        </Button>
      </div>

      <div v-if="discount > 0" class="flex items-center justify-between">
        <span class="text-muted-foreground">{{ coupon || t('portal.buy.discount') }}</span>
        <span class="font-medium text-primary">-{{ symbol }}{{ formatPrice(discount) }}</span>
      </div>
    </div>

    <Separator />

    <div class="flex items-baseline justify-between">
      <span class="text-sm font-medium text-muted-foreground">{{ t('portal.buy.grandTotal') }}</span>
      <span class="text-xl font-bold text-foreground">
        {{ total === undefined ? '--' : symbol + formatPrice(total) }}
        <span class="ms-1 text-xs font-normal text-muted-foreground">{{ currencyCode }}</span>
      </span>
    </div>

    <Button
      v-if="!hideSubmit"
      class="mt-auto h-11 w-full"
      :disabled="loading || total === undefined"
      @click="emit('submit')"
    >
      <Check v-if="!loading" class="me-2 size-4" />
      {{ submitLabel }}
    </Button>
  </aside>
</template>
```

- [ ] **Step 2: 跑全套检查**

```bash
npm run ts:check
npm run lint
npm run build
```

Expected：三条命令全部退出码 0。

- [ ] **Step 3: 手动验证**

`npm run dev`，打开 `/portal/buy/100g`。
Expected：右侧概览卡片显示大号靛蓝总价、套餐名与「购买 100G 服务 N 天（一次性付款，不自动续费）」描述、小计行、优惠码输入框、总计行、底部下单按钮。
输入一个无效优惠码回车，Expected：弹出红色 toast（不再是 Element 的消息条）。
切暗色，Expected：卡片背景、文字、分隔线全部跟随变化，无残留浅灰硬编码色。

- [ ] **Step 4: 提交**

```bash
git add darknight/dashboard/src/views/portal/Buy/components/OrderSummary.vue
git commit -m "refactor(dashboard): rebuild OrderSummary with design tokens"
```

---

### Task 6: 重写 PayPalCardForm 并让 iframe 跟随主题

**Files:**
- Create: `darknight/dashboard/src/views/portal/Buy/components/paypalFieldStyle.ts`
- Modify: `darknight/dashboard/src/views/portal/Buy/components/PayPalCardForm.vue`（整文件替换）

**Interfaces:**
- Consumes: Task 1 的 `--paypal-field-color` `--paypal-field-placeholder` `--paypal-field-focus` `--paypal-field-invalid`；Task 2 的 `Button` `Label`；Task 3 的 `LoadingOverlay`
- Produces:
  - `readPayPalFieldStyle(): Record<string, Record<string, string>>`，从 `paypalFieldStyle.ts` 导出
  - `PayPalCardForm` 组件，props / emits / `defineExpose({ submitPayment })` 与改造前完全一致

**为什么需要单独的样式模块：** PayPal CardFields 渲染在 iframe 内，Tailwind 的 class 无法穿透，输入框的字号与颜色只能在初始化时通过 `style` 对象传入具体色值。传进去的必须是十六进制，所以 Task 1 才额外定义了四个 `--paypal-*` hex 变量。

- [ ] **Step 1: 创建 `paypalFieldStyle.ts`**

```ts
/**
 * PayPal CardFields 渲染在 iframe 内，Tailwind 无法穿透，
 * 字体与颜色只能在初始化时以具体色值传入。这里读的是 globals.css 中
 * 专为此用途定义的十六进制变量（iframe 内不保证支持 oklch）。
 */
export function readPayPalFieldStyle(): Record<string, Record<string, string>> {
  const css = getComputedStyle(document.documentElement)
  const read = (name: string, fallback: string) => css.getPropertyValue(name).trim() || fallback

  const color = read('--paypal-field-color', '#18181b')
  const placeholder = read('--paypal-field-placeholder', '#a1a1aa')
  const focus = read('--paypal-field-focus', '#6366f1')
  const invalid = read('--paypal-field-invalid', '#ef4444')

  return {
    input: {
      color,
      'font-size': '14px',
      'font-family':
        "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
      padding: '0'
    },
    '::placeholder': { color: placeholder },
    ':focus': { color: focus },
    '.invalid': { color: invalid }
  }
}
```

- [ ] **Step 2: 整文件替换 `PayPalCardForm.vue`**

相对改造前的三处行为变化：加载遮罩换成 `LoadingOverlay`、字段初始化时传入 `style`、新增对主题的 watch。
`settled` / `errorNotified` / `destroyed` 三个状态标志用于防止扣款成功后 SDK 重复报错，逻辑原样保留。

```vue
<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { loadScript, type PayPalCardFieldsComponent } from '@paypal/paypal-js'
import { capturePortalOrder, fetchPayPalConfig, type PortalOrder } from '@/api/portal/orders'
import { resolvePayPalSdkError, resolvePortalApiError } from '@/utils/portalError'
import { useThemeStore } from '@/store/modules/theme'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import LoadingOverlay from '@/components/LoadingOverlay/index.vue'
import { currencySymbol, formatPrice } from '../plans'
import { readPayPalFieldStyle } from './paypalFieldStyle'

const props = defineProps<{
  orderId: string
  paypalOrderId: string
  amount: number
  currency: string
}>()

const emit = defineEmits<{
  success: [order: PortalOrder]
  error: [message: string]
}>()

const { t } = useI18n()
const theme = useThemeStore()
const loading = ref(true)
const paying = ref(false)
const ready = ref(false)
const cardFields = ref<PayPalCardFieldsComponent | null>(null)

let destroyed = false
/**
 * 扣款成功后 PayPal SDK 仍可能回调 onError 或让 submit() reject（订单已不可再支付），
 * 此时不能再向用户报错。同一次尝试内也只提示一次，避免多条通道重复弹窗。
 */
let settled = false
let errorNotified = false
let renderedFields: { close: () => void }[] = []

function reportError(message: string) {
  if (settled || destroyed || errorNotified) return
  errorNotified = true
  emit('error', message)
}

function reportPayPalError(err: unknown) {
  // 原始错误体比映射后的文案信息量大得多，排查时需要。
  console.error('[PayPal] card payment failed', err)
  reportError(resolvePayPalSdkError(err, t))
}

const FIELD_SELECTORS = [
  '#paypal-card-name',
  '#paypal-card-number',
  '#paypal-card-expiry',
  '#paypal-card-cvv'
]

/** 换新 PayPal 订单时会重新 render，先拆掉上一轮的 iframe 免得叠加。 */
function teardownFields() {
  for (const field of renderedFields) {
    try {
      field.close()
    } catch {
      // SDK 已卸载时 close 会抛，此时容器清空即可。
    }
  }
  renderedFields = []
  for (const selector of FIELD_SELECTORS) {
    const host = document.querySelector(selector)
    if (host) host.innerHTML = ''
  }
  cardFields.value = null
}

async function initCardFields() {
  loading.value = true
  ready.value = false
  errorNotified = false
  teardownFields()

  try {
    const config = await fetchPayPalConfig()
    if (!config.enabled || !config.client_id) {
      reportError(t('portal.buy.paypalNotConfigured'))
      return
    }

    const paypal = await loadScript({
      clientId: config.client_id,
      components: 'card-fields',
      currency: config.currency
    })

    if (!paypal?.CardFields || destroyed) return

    const fields = paypal.CardFields({
      style: readPayPalFieldStyle(),
      createOrder: () => Promise.resolve(props.paypalOrderId),
      onApprove: async () => {
        paying.value = true
        try {
          const { order } = await capturePortalOrder(props.orderId)
          // 保持按钮 loading 直到父组件切走表单，避免重复提交。
          settled = true
          emit('success', order)
        } catch (err) {
          paying.value = false
          reportError(resolvePortalApiError(err, t))
        }
      },
      onError: (err: unknown) => {
        if (settled) return
        paying.value = false
        reportPayPalError(err)
      }
    })

    if (!fields.isEligible()) {
      reportError(t('portal.buy.cardNotEligible'))
      return
    }

    cardFields.value = fields
    const instances = [
      fields.NameField({}),
      fields.NumberField({}),
      fields.ExpiryField({}),
      fields.CVVField({})
    ]
    renderedFields = instances
    await Promise.all(instances.map((field, i) => field.render(FIELD_SELECTORS[i])))

    if (!destroyed) {
      ready.value = true
    }
  } catch {
    reportError(t('portal.buy.paypalLoadFailed'))
  } finally {
    if (!destroyed) {
      loading.value = false
    }
  }
}

async function submitPayment() {
  if (!cardFields.value || paying.value || settled) return
  paying.value = true
  errorNotified = false
  try {
    await cardFields.value.submit()
  } catch (err) {
    if (settled) return
    paying.value = false
    reportPayPalError(err)
  }
}

watch(
  () => props.paypalOrderId,
  () => {
    if (props.paypalOrderId) {
      initCardFields()
    }
  }
)

// iframe 内的样式在初始化时就固定了，切主题必须重建。
// 重建会清空已填的卡号，所以支付进行中一律跳过，等这一轮结束。
watch(
  () => theme.mode,
  () => {
    if (!props.paypalOrderId || paying.value || settled || destroyed) return
    initCardFields()
  }
)

onMounted(() => {
  if (props.paypalOrderId) {
    initCardFields()
  }
})

onBeforeUnmount(() => {
  destroyed = true
  teardownFields()
})

defineExpose({ submitPayment })
</script>

<template>
  <LoadingOverlay :loading="loading">
    <div class="space-y-4">
      <div class="space-y-2">
        <Label for="paypal-card-number">{{ t('portal.buy.cardNumber') }}</Label>
        <div
          id="paypal-card-number"
          class="h-11 rounded-md border border-input bg-background px-3 py-2 transition-colors focus-within:border-ring focus-within:ring-[3px] focus-within:ring-ring/30"
        />
      </div>
      <div class="space-y-2">
        <Label for="paypal-card-name">{{ t('portal.buy.cardName') }}</Label>
        <div
          id="paypal-card-name"
          class="h-11 rounded-md border border-input bg-background px-3 py-2 transition-colors focus-within:border-ring focus-within:ring-[3px] focus-within:ring-ring/30"
        />
      </div>
      <div class="grid grid-cols-2 gap-4">
        <div class="space-y-2">
          <Label for="paypal-card-expiry">{{ t('portal.buy.cardExpiry') }}</Label>
          <div
            id="paypal-card-expiry"
            class="h-11 rounded-md border border-input bg-background px-3 py-2 transition-colors focus-within:border-ring focus-within:ring-[3px] focus-within:ring-ring/30"
          />
        </div>
        <div class="space-y-2">
          <Label for="paypal-card-cvv">{{ t('portal.buy.cardCvv') }}</Label>
          <div
            id="paypal-card-cvv"
            class="h-11 rounded-md border border-input bg-background px-3 py-2 transition-colors focus-within:border-ring focus-within:ring-[3px] focus-within:ring-ring/30"
          />
        </div>
      </div>

      <Button class="h-11 w-full text-base" :disabled="!ready || paying" @click="submitPayment">
        {{ t('portal.buy.payAmount', { amount: currencySymbol(currency) + formatPrice(amount) }) }}
      </Button>
      <p class="text-center text-xs text-muted-foreground">
        {{ t('portal.buy.poweredByPayPal') }}
      </p>
    </div>
  </LoadingOverlay>
</template>
```

- [ ] **Step 3: 跑全套检查**

```bash
npm run ts:check
npm run lint
npm run build
```

Expected：三条命令全部退出码 0。若 `ts:check` 报 `CardFields` 的 `style` 属性类型不匹配，
在 `PayPalCardForm.vue` 的调用处改成 `style: readPayPalFieldStyle() as never`，
只放宽调用点的类型，不要改动 `readPayPalFieldStyle()` 的返回结构 —— 那个结构是 PayPal SDK 运行时要求的。

- [ ] **Step 4: 手动验证（需要一个 pending 订单）**

在 `/portal/buy` 走完下单拿到订单页。
Expected：四个输入框是圆角浅边框，点击时边框变靛蓝且有一圈柔和外发光；输入框内的文字颜色是深灰而非黑。
切暗色，Expected：iframe 内的文字变浅色可读（而不是暗底黑字），输入框重新渲染。
输入几位卡号后再切主题，Expected：卡号被清空（这是已知且接受的行为，重建 iframe 的必然结果）。

- [ ] **Step 5: 提交**

```bash
git add darknight/dashboard/src/views/portal/Buy/components/PayPalCardForm.vue darknight/dashboard/src/views/portal/Buy/components/paypalFieldStyle.ts
git commit -m "refactor(dashboard): restyle PayPal card fields and follow theme changes"
```

---

### Task 7: 结算页改为居中独立面板

**Files:**
- Modify: `darknight/dashboard/src/router/portal.ts:83-92`
- Modify: `darknight/dashboard/src/views/portal/Orders/Detail.vue`（整文件替换）

**Interfaces:**
- Consumes: Task 2 的 `Button` `Alert` `AlertDescription`；Task 3 的 `useConfirm` `LoadingOverlay` 与 `toast`；Task 4 的 `portal.buy.stepOrder` `portal.buy.stepPayment`；Task 5 的 `OrderSummary`（用 `variant="panel"`）；Task 6 的 `PayPalCardForm`
- Produces: 路由 `portal-order-detail` 变为顶层路由，路径仍是 `/portal/orders/:orderId`，`meta` 仍带 `authType: 'user'`

- [ ] **Step 1: 把 `portal-order-detail` 从 `UserLayout` 的 children 移出**

在 `src/router/portal.ts` 中删掉 `children` 数组里第 83-92 行的那一项，并在 `portalRoutes` 顶层数组中、`/portal` 那一项**之前**插入：

```ts
  {
    path: '/portal/orders/:orderId',
    name: 'portal-order-detail',
    component: () => import('@/views/portal/Orders/Detail.vue'),
    meta: {
      title: 'portal.buy.orderDetailTitle',
      zone: 'portal',
      authType: 'user',
      hideInMenu: true
    }
  },
```

必须排在 `/portal` 之前，否则 `/portal` 那条带 children 的记录会先匹配。

`UserLayout/index.vue` 第 58-60 行的 `activeMenu` 里有 `if (String(route.name).startsWith('portal-order')) return 'portal-orders'`，
结算页不再套 UserLayout，这行对它不再生效，但对 `/portal/orders` 列表页仍然需要，**保持不动**。

- [ ] **Step 2: 整文件替换 `Orders/Detail.vue`**

```vue
<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { CircleCheckBig, X } from 'lucide-vue-next'
import { toast } from 'vue-sonner'
import OrderSummary from '../Buy/components/OrderSummary.vue'
import PayPalCardForm from '../Buy/components/PayPalCardForm.vue'
import {
  closePortalOrder,
  fetchPortalOrder,
  formatOrderTime,
  preparePortalOrderPayment,
  type PortalOrder
} from '@/api/portal/orders'
import { resolvePortalApiError } from '@/utils/portalError'
import { useConfirm } from '@/composables/useConfirm'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
import LoadingOverlay from '@/components/LoadingOverlay/index.vue'
import { getCycleLabelKey, getPlanMeta } from '../Buy/plans'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const { confirm } = useConfirm()

const orderId = computed(() => String(route.params.orderId || ''))
const order = ref<PortalOrder | null>(null)
const loading = ref(true)
const preparingPayment = ref(false)
const paymentError = ref('')

const planName = computed(() =>
  order.value ? (getPlanMeta(order.value.plan_id)?.name ?? order.value.plan_id) : ''
)
const cycleLabel = computed(() => (order.value ? t(getCycleLabelKey(order.value.cycle_id)) : ''))
const isPaid = computed(() => order.value?.status === 'paid')

async function loadOrder() {
  loading.value = true
  paymentError.value = ''
  try {
    order.value = await fetchPortalOrder(orderId.value)
    if (order.value.status === 'closed') {
      router.replace({ name: 'portal-orders' })
      return
    }
    if (order.value.status === 'pending' && !order.value.paypal_order_id) {
      await ensurePaymentReady()
    }
  } catch (err) {
    toast.error(resolvePortalApiError(err, t))
    router.replace({ name: 'portal-orders' })
  } finally {
    loading.value = false
  }
}

async function ensurePaymentReady(refresh = false) {
  preparingPayment.value = true
  paymentError.value = ''
  try {
    order.value = await preparePortalOrderPayment(orderId.value, { refresh })
  } catch (err) {
    paymentError.value = resolvePortalApiError(err, t)
  } finally {
    preparingPayment.value = false
  }
}

watch(orderId, loadOrder, { immediate: true })

async function onCloseOrder() {
  try {
    await confirm({
      title: t('portal.buy.closeOrder'),
      description: t('portal.buy.closeOrderConfirm'),
      destructive: true
    })
  } catch {
    return
  }

  try {
    await closePortalOrder(orderId.value)
    toast.success(t('portal.buy.closeOrderSuccess'))
    router.push({ name: 'portal-orders' })
  } catch (err) {
    toast.error(resolvePortalApiError(err, t))
  }
}

function onPaymentSuccess(paid: PortalOrder) {
  order.value = paid
  paymentError.value = ''
  toast.success(t('portal.buy.paymentSuccess'))
}

async function onPaymentError(message: string) {
  toast.error(message)

  // 失败的那次尝试已经把 PayPal 订单用掉了，必须换一个新的，
  // 否则下一次提交是对着作废订单打，永远失败。
  try {
    order.value = await fetchPortalOrder(orderId.value)
  } catch {
    return
  }
  if (order.value.status === 'pending') {
    await ensurePaymentReady(true)
  }
}
</script>

<template>
  <div class="min-h-screen bg-muted px-4 py-10">
    <LoadingOverlay :loading="loading" class="mx-auto w-full max-w-5xl">
      <div
        v-if="order"
        class="overflow-hidden rounded-2xl border border-border bg-card shadow-xl md:grid md:grid-cols-[minmax(0,380px)_minmax(0,1fr)]"
      >
        <OrderSummary
          :plan-id="order.plan_id"
          :cycle-id="order.cycle_id"
          :coupon="order.coupon || undefined"
          :amount="order.amount"
          :discount="order.discount"
          :currency="order.currency"
          :submit-label="t('portal.buy.checkout')"
          variant="panel"
          hide-submit
          readonly-coupon
        />

        <div class="p-8">
          <div v-if="isPaid" class="flex h-full flex-col items-center justify-center gap-4 text-center">
            <CircleCheckBig class="size-14 text-primary" />
            <h2 class="text-xl font-semibold text-foreground">{{ t('portal.buy.paymentSuccess') }}</h2>
            <p class="max-w-sm text-sm text-muted-foreground">
              {{ t('portal.buy.paymentSuccessHint', { plan: planName, cycle: cycleLabel }) }}
            </p>
            <div class="mt-2 flex flex-wrap items-center justify-center gap-3">
              <Button @click="router.push({ name: 'portal-dashboard' })">
                {{ t('portal.buy.goDashboard') }}
              </Button>
              <Button variant="outline" @click="router.push({ name: 'portal-docs' })">
                {{ t('portal.buy.goDocs') }}
              </Button>
            </div>
          </div>

          <template v-else>
            <div class="mb-8 flex items-center gap-2 text-sm">
              <span class="text-muted-foreground">{{ t('portal.buy.stepOrder') }}</span>
              <span class="text-muted-foreground">&rsaquo;</span>
              <span class="font-semibold text-primary">{{ t('portal.buy.stepPayment') }}</span>
              <Button
                v-if="order.status === 'pending'"
                variant="ghost"
                size="icon"
                class="ms-auto text-muted-foreground"
                @click="onCloseOrder"
              >
                <X class="size-4" />
              </Button>
            </div>

            <LoadingOverlay v-if="order.status === 'pending'" :loading="preparingPayment">
              <PayPalCardForm
                v-if="order.paypal_order_id"
                :order-id="order.id"
                :paypal-order-id="order.paypal_order_id"
                :amount="order.amount"
                :currency="order.currency"
                @success="onPaymentSuccess"
                @error="onPaymentError"
              />
              <div v-else-if="paymentError" class="space-y-3">
                <Alert variant="destructive">
                  <AlertDescription>{{ paymentError }}</AlertDescription>
                </Alert>
                <Button variant="outline" @click="ensurePaymentReady(true)">
                  {{ t('portal.buy.retryPayment') }}
                </Button>
              </div>
            </LoadingOverlay>

            <Alert v-else-if="order.status === 'failed'" variant="destructive">
              <AlertDescription>{{ t('portal.buy.paymentFailed') }}</AlertDescription>
            </Alert>

            <div class="mt-8 border-t border-border pt-4 text-xs text-muted-foreground">
              {{ t('portal.buy.orderNo') }} {{ order.id }} ·
              {{ formatOrderTime(order.created_at) }}
              <template v-if="order.paid_at">
                · {{ t('portal.buy.paidAt') }} {{ formatOrderTime(order.paid_at) }}
              </template>
            </div>
          </template>
        </div>
      </div>
    </LoadingOverlay>
  </div>
</template>
```

- [ ] **Step 3: 跑全套检查**

```bash
npm run ts:check
npm run lint
npm run build
```

Expected：三条命令全部退出码 0。若 `ts:check` 报 `LoadingOverlay` 不接受 `class`，
说明该组件根节点没有透传 attrs —— Vue 单根组件默认透传，无需改动；若报错请检查根节点是否唯一。

- [ ] **Step 4: 手动验证**

从 `/portal/buy` 下单进入订单页。
Expected：整页浅灰底，中间一个大圆角带阴影的面板，无侧边栏无顶栏；左栏浅色区显示金额概览，右栏显示「订单信息 › 付款」步骤条、卡片表单、支付按钮，右上角是一个低调的关闭图标按钮，底部一行小字是订单号与创建时间。
点关闭图标，Expected：弹出 shadcn 的确认对话框（不是 Element 的 MessageBox），确认后跳回订单列表。
把窗口宽度收到 900px 以下，Expected：两栏堆叠成上下单列。
切波斯语，Expected：步骤条与关闭按钮镜像到左侧，文字右对齐，布局不错位。

- [ ] **Step 5: 提交**

```bash
git add darknight/dashboard/src/router/portal.ts darknight/dashboard/src/views/portal/Orders/Detail.vue
git commit -m "feat(dashboard): rebuild checkout as standalone centered panel"
```

---

### Task 8: 重写套餐列表页与配置页

**Files:**
- Modify: `darknight/dashboard/src/views/portal/Buy/index.vue`（整文件替换）
- Modify: `darknight/dashboard/src/views/portal/Buy/Configure.vue`（整文件替换）

**Interfaces:**
- Consumes: Task 2 的 `Button` `Alert` `AlertDescription` `Skeleton`；Task 3 的 `toast`；Task 5 的 `OrderSummary`（用默认 `variant="aside"`）
- Produces: 无新对外接口

- [ ] **Step 1: 整文件替换 `Buy/index.vue`**

```vue
<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { Check } from 'lucide-vue-next'
import { currencySymbol, formatPrice, type PlanFilter } from './plans'
import { usePlanCatalog, type PricedPlan } from './usePlanCatalog'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Skeleton } from '@/components/ui/skeleton'
import { cn } from '@/lib/utils'

const { t } = useI18n()
const router = useRouter()

const activeFilter = ref<PlanFilter>('all')
const { currency, filterPlans, isLoading, isError } = usePlanCatalog()

const filters: { id: PlanFilter; labelKey: string }[] = [
  { id: 'all', labelKey: 'portal.buy.filter.all' },
  { id: 'period', labelKey: 'portal.buy.filter.period' },
  { id: 'traffic', labelKey: 'portal.buy.filter.traffic' }
]

const plans = computed(() => filterPlans(activeFilter.value))

function displayCycle(plan: PricedPlan) {
  return plan.cycles.find((cycle) => cycle.id === plan.displayCycleId) ?? plan.cycles[0]
}

function subscribe(planId: string) {
  router.push({ name: 'portal-buy-configure', params: { planId } })
}
</script>

<template>
  <div class="max-w-6xl">
    <h2 class="mb-5 text-2xl font-bold tracking-tight text-foreground">
      {{ t('portal.buy.choosePlan') }}
    </h2>

    <div class="mb-6 inline-flex rounded-lg bg-muted p-1">
      <button
        v-for="item in filters"
        :key="item.id"
        type="button"
        :class="
          cn(
            'rounded-md px-4 py-1.5 text-sm font-medium transition-colors',
            activeFilter === item.id
              ? 'bg-background text-foreground shadow-sm'
              : 'text-muted-foreground hover:text-foreground'
          )
        "
        @click="activeFilter = item.id"
      >
        {{ t(item.labelKey) }}
      </button>
    </div>

    <Alert v-if="isError" variant="destructive" class="mb-4">
      <AlertDescription>{{ t('portal.buy.plansLoadFailed') }}</AlertDescription>
    </Alert>

    <div v-if="isLoading" class="grid gap-5 lg:grid-cols-3">
      <Skeleton v-for="i in 3" :key="i" class="h-96 rounded-xl" />
    </div>

    <div v-else class="grid items-stretch gap-5 lg:grid-cols-3">
      <div
        v-for="plan in plans"
        :key="plan.id"
        class="flex flex-col rounded-xl border border-border bg-card p-7 transition-shadow hover:shadow-lg"
      >
        <p class="text-2xl font-bold text-foreground">{{ plan.name }}</p>
        <div class="mt-3 flex items-baseline gap-1">
          <span class="text-lg font-semibold text-foreground">{{ currencySymbol(currency) }}</span>
          <span class="text-4xl font-bold leading-none tracking-tight text-foreground">
            {{ formatPrice(displayCycle(plan).price) }}
          </span>
          <span class="text-sm text-muted-foreground">{{ t(displayCycle(plan).labelKey) }}</span>
        </div>
        <ul class="mt-6 flex-1 space-y-2.5">
          <li
            v-for="key in plan.featureKeys"
            :key="key"
            class="flex items-start gap-2 text-sm leading-relaxed text-muted-foreground"
          >
            <Check class="mt-0.5 size-4 shrink-0 text-primary" />
            <span>{{ t(key) }}</span>
          </li>
        </ul>
        <Button class="mt-7 h-11 w-full" @click="subscribe(plan.id)">
          {{ t('portal.buy.subscribeNow') }}
        </Button>
      </div>
    </div>
  </div>
</template>
```

- [ ] **Step 2: 整文件替换 `Buy/Configure.vue`**

```vue
<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { Check } from 'lucide-vue-next'
import { toast } from 'vue-sonner'
import { createPortalOrder } from '@/api/portal/orders'
import { resolvePortalApiError } from '@/utils/portalError'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { cn } from '@/lib/utils'
import OrderSummary from './components/OrderSummary.vue'
import { currencySymbol, formatPrice, type BillingCycleId } from './plans'
import { usePlanCatalog } from './usePlanCatalog'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()

const { currency, getPlan, isLoading, isError } = usePlanCatalog()

const planId = computed(() => String(route.params.planId || ''))
const plan = computed(() => getPlan(planId.value))
const selectedCycleId = ref<BillingCycleId>('yearly')
const coupon = ref('')
const submitting = ref(false)

watch(
  plan,
  (value) => {
    if (value?.cycles[0]) {
      selectedCycleId.value = value.cycles[0].id
    }
  },
  { immediate: true }
)

watch([planId, isLoading], () => {
  if (!isLoading.value && !plan.value) {
    router.replace({ name: 'portal-buy' })
  }
})

async function placeOrder() {
  if (!plan.value) return
  submitting.value = true
  try {
    const order = await createPortalOrder({
      plan_id: plan.value.id,
      cycle_id: selectedCycleId.value,
      coupon: coupon.value.trim() || undefined
    })
    router.push({ name: 'portal-order-detail', params: { orderId: order.id } })
  } catch (err) {
    toast.error(resolvePortalApiError(err, t))
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <Alert v-if="isError" variant="destructive">
    <AlertDescription>{{ t('portal.buy.plansLoadFailed') }}</AlertDescription>
  </Alert>
  <div v-else-if="plan" class="flex flex-col items-start gap-5 lg:flex-row">
    <div class="min-w-0 flex-1 space-y-4">
      <div class="rounded-xl border border-border bg-card p-7">
        <p class="mb-4 text-2xl font-bold text-foreground">{{ plan.name }}</p>
        <ul class="space-y-2.5">
          <li
            v-for="key in plan.featureKeys"
            :key="key"
            class="flex items-start gap-2 text-sm leading-relaxed text-muted-foreground"
          >
            <Check class="mt-0.5 size-4 shrink-0 text-primary" />
            <span>{{ t(key) }}</span>
          </li>
        </ul>
      </div>

      <div class="rounded-xl border border-border bg-card p-7">
        <p class="mb-4 text-base font-semibold text-foreground">
          {{ t('portal.buy.paymentCycle') }}
        </p>
        <div class="space-y-3">
          <button
            v-for="cycle in plan.cycles"
            :key="cycle.id"
            type="button"
            :class="
              cn(
                'flex w-full items-center justify-between rounded-lg border px-5 py-4 text-[15px] transition-colors',
                selectedCycleId === cycle.id
                  ? 'border-primary bg-primary/5 text-foreground ring-1 ring-primary'
                  : 'border-border text-foreground hover:border-primary/40'
              )
            "
            @click="selectedCycleId = cycle.id"
          >
            <span>{{ t(cycle.labelKey) }}</span>
            <span class="font-semibold">
              {{ currencySymbol(currency) }}{{ formatPrice(cycle.price) }}
            </span>
          </button>
        </div>
      </div>
    </div>

    <OrderSummary
      :plan-id="plan.id"
      :cycle-id="selectedCycleId"
      :coupon="coupon"
      :loading="submitting"
      :submit-label="t('portal.buy.placeOrder')"
      @update:coupon="coupon = $event"
      @submit="placeOrder"
    />
  </div>
</template>
```

- [ ] **Step 3: 确认改造范围内已无写死颜色**

```bash
cd darknight/dashboard
rg "#[0-9a-fA-F]{3,8}\b" src/views/portal/Buy src/views/portal/Orders/Detail.vue
```

Expected：无输出。

- [ ] **Step 4: 跑全套检查**

```bash
npm run ts:check
npm run lint
npm run build
```

Expected：三条命令全部退出码 0。

- [ ] **Step 5: 提交**

```bash
git add darknight/dashboard/src/views/portal/Buy/index.vue darknight/dashboard/src/views/portal/Buy/Configure.vue
git commit -m "refactor(dashboard): rebuild plan list and configure pages"
```

---

### Task 9: 清理废弃文案并做全量验收

**Files:**
- Modify: `darknight/dashboard/src/locales/zh.json`
- Modify: `darknight/dashboard/src/locales/en.json`
- Modify: `darknight/dashboard/src/locales/ru.json`
- Modify: `darknight/dashboard/src/locales/fa.json`

**Interfaces:**
- Consumes: 前八个任务的全部产出
- Produces: 无

- [ ] **Step 1: 找出已无引用的文案键**

PowerShell：

```powershell
cd darknight/dashboard
'portal.buy.productInfo','portal.buy.productTraffic','portal.buy.orderInfo','portal.buy.paymentMethod','portal.buy.createdAt' | ForEach-Object { "== $_"; rg -c $_ src --glob '!src/locales/*' }
```

Expected：`portal.buy.productTraffic`、`portal.buy.orderInfo`、`portal.buy.paymentMethod` 三个应无匹配（结算页已不再用这些标题）。
`portal.buy.productInfo` 必须仍有匹配（订单列表页 `Orders/index.vue` 的列标题），**禁止删除**。
`portal.buy.createdAt` 应仍有匹配（Task 7 的底部小字用到了）。

- [ ] **Step 2: 从四个语言文件删除确认无引用的键**

只删 Step 1 中确认无匹配的那几个。任何仍有匹配的键都不许删。

- [ ] **Step 3: 再次验证四个文件的 key 集合一致**

```bash
node -e "const a=['zh','en','ru','fa'].map(l=>({l,k:Object.keys(require('./src/locales/'+l+'.json')).filter(x=>x.startsWith('portal.buy.'))})); const base=new Set(a[0].k); a.forEach(x=>{const miss=[...base].filter(k=>!x.k.includes(k)); const extra=x.k.filter(k=>!base.has(k)); console.log(x.l, 'missing:', miss, 'extra:', extra)})"
```

Expected：四行输出的 `missing` 与 `extra` 都是 `[]`。

- [ ] **Step 4: 跑全套检查**

```bash
npm run ts:check
npm run lint
npm run build
```

Expected：三条命令全部退出码 0。

- [ ] **Step 5: 走完 spec 的手动验收清单**

`npm run dev`，逐项确认：

1. 结算全链路：选套餐 → 配置周期 → 应用优惠码 → 下单 → 填卡 → 支付成功。
2. 支付失败后重试，确认换发了新的 PayPal 订单且能再次提交。
3. 亮色 / 暗色各走一遍，重点确认 PayPal iframe 内的文字在暗色下可读。
4. 支付过程中切换主题，确认不会清空已填卡号。
5. 中 / 英 / 俄 / 波斯四种语言，波斯语确认 RTL 下布局不错位。
6. 窄屏（≤960px）下结算面板正确堆叠为单列。
7. admin 四个页面（`/admin/user`、`/admin/node`、`/admin/host`、`/admin/setting`）的表格、表单、弹窗、分页无视觉破坏。

任何一项不通过就地修复，修完重跑 Step 4。

- [ ] **Step 6: 提交**

```bash
git add darknight/dashboard/src/locales
git commit -m "chore(dashboard): drop unused checkout copy after redesign"
```

---

## 后续 spec 的入口

本计划完成后，Element Plus 仍在 `package.json` 中，`ElementPlusResolver` 仍然启用，
`main.ts` 仍引入其 CSS。门户其余页面、官网、认证、admin 都还在用 Element Plus。
下一步按 spec 的拆解表继续 spec 2（门户外壳与其余门户页）。
