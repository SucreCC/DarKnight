# 门户壳层 + 认证 + 门户主页面改版 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把用户门户壳层、登录/注册、仪表盘、文档、订单列表迁移到与 `/portal/buy` 一致的 Tailwind + shadcn 紫主色白卡片风格。

**Architecture:** 先补齐 `DropdownMenu`，再重写 `UserLayout`（去掉 Element 菜单/下拉与青绿顶栏），随后按页替换 Element 控件为已有 `Button`/`Card`/`Input`/`Label`/`Alert`/`Badge`/`Skeleton`，表单校验改为页面内轻量函数。Element Plus 本批继续保留给 Admin / `LanguageSwitch` 等未迁页面。

**Tech Stack:** Vue 3.5、Vite、TypeScript、Tailwind CSS v4、shadcn-vue（Reka UI）、lucide-vue-next、vue-sonner、vue-i18n 10、@tanstack/vue-query 5

**Spec:** `docs/superpowers/specs/2026-08-31-portal-shell-and-pages-design.md`

## Global Constraints

- 所有命令在 `e:\kai\DarKnight\darknight\dashboard` 下执行，包管理器用 `npm`。
- 设计令牌沿用 `src/assets/css/globals.css`；主色亮色 `oklch(0.585 0.233 277.1)`，暗色 `oklch(0.66 0.19 277.1)`。
- 本计划触及的文件内不得残留写死颜色（`#20a397`、`#1b8c82`、`#1b8f84`、`#303133`、`#606266`、`#909399`、`#dcdfe6`、`#e4e7ed`、`#f5f7fa`、`#eef2f6`），一律改用令牌类（`bg-primary`、`text-muted-foreground`、`border-border`、`bg-muted` 等）。
- 间距/定位用逻辑属性（`ms-`/`me-`/`ps-`/`pe-`/`start-`/`end-`/`text-start`/`text-end`），禁止物理方向类；项目支持 RTL。
- 不改后端、路由 name、购买流程、业务 API。
- 本批不做：官网、Admin、占位页内容、卸载 Element Plus、移动端侧栏抽屉。
- `LanguageSwitch` 本批可继续用 Element（共享组件，避免拖进 admin）；顶栏里允许暂时并存。
- 无测试框架；验收 = `npm run ts:check` + `npm run lint` + `npm run build`，再加该任务手动检查项。
- i18n 为扁平点号键；本批尽量不新增 key；若必须新增，同时写入 `zh.json`、`en.json`、`ru.json`、`fa.json`。
- 每个任务结束提交一次；提交信息英文，格式 `feat(dashboard): ...` / `refactor(dashboard): ...`。

## File Map

| 文件 | 职责 |
|------|------|
| `src/components/ui/dropdown-menu/*` | 顶栏用户菜单 |
| `src/layout/UserLayout/index.vue` | 门户壳 |
| `src/router/portal.ts` | `meta.icon` 改为 lucide 名 |
| `src/views/auth/Login/index.vue` | 登录页 |
| `src/views/portal/Register/index.vue` | 注册页 |
| `src/views/portal/Register/components/SlideCaptchaDialog.vue` | 滑块验证码外层对齐 |
| `src/views/portal/Dashboard/index.vue` | 仪表盘 |
| `src/views/portal/Docs/index.vue` | 文档列表 |
| `src/views/portal/Docs/Detail.vue` | 文档详情 |
| `src/views/portal/Orders/index.vue` | 订单列表 |

---

### Task 1: 补齐 DropdownMenu

**Files:**
- Create: `darknight/dashboard/src/components/ui/dropdown-menu/*`（由 CLI 生成）

**Interfaces:**
- Consumes: 现有 `components.json`、`@/lib/utils`、`reka-ui`
- Produces: 可从 `@/components/ui/dropdown-menu` 导入 `DropdownMenu`、`DropdownMenuTrigger`、`DropdownMenuContent`、`DropdownMenuItem`、`DropdownMenuLabel`、`DropdownMenuSeparator` 等

- [ ] **Step 1: 用 shadcn-vue 添加组件**

```bash
cd darknight/dashboard
npx shadcn-vue@latest add dropdown-menu
```

Expected：出现 `src/components/ui/dropdown-menu/`，内含 `index.ts` 与若干 `.vue`。

- [ ] **Step 2: 确认导出**

打开 `src/components/ui/dropdown-menu/index.ts`，确认至少导出：

- `DropdownMenu`
- `DropdownMenuTrigger`
- `DropdownMenuContent`
- `DropdownMenuItem`

若 CLI 命名不同，以实际 `index.ts` 为准，后续 Task 2 按实际导出名 import。

- [ ] **Step 3: 类型检查**

```bash
npm run ts:check
```

Expected：PASS（无新增错误）。

- [ ] **Step 4: Commit**

```bash
git add src/components/ui/dropdown-menu
git commit -m "feat(dashboard): add shadcn dropdown-menu for portal header"
```

---

### Task 2: 重写 UserLayout + 路由图标

**Files:**
- Modify: `darknight/dashboard/src/layout/UserLayout/index.vue`（整文件替换）
- Modify: `darknight/dashboard/src/router/portal.ts`（各 `meta.icon` 字符串）

**Interfaces:**
- Consumes: Task 1 的 DropdownMenu；`portalRoutes`；`fetchPortalMe`；`LanguageSwitch`；lucide icons
- Produces: 白顶栏 + 紫高亮侧栏布局；`meta.icon` 为 lucide 组件名字符串

- [ ] **Step 1: 更新 `portal.ts` 的 icon 名**

把 children 里 `meta.icon` 从 Element 名改为 lucide 名：

| route name | 新 icon |
|---|---|
| portal-dashboard | `Gauge` |
| portal-docs | `FileText` |
| portal-buy | `ShoppingCart` |
| portal-nodes | `Monitor` |
| portal-orders | `List` |
| portal-invite | `UserPlus` |
| portal-profile | `User` |
| portal-tickets | `Headset` |
| portal-traffic | `Activity` |

只改 `icon` 字段字符串，其它 meta 不动。

- [ ] **Step 2: 重写 `UserLayout/index.vue`**

整文件替换为（保留原 script 业务逻辑：menuGroups、activeMenu、pageTitle、logout、fetchPortalMe）：

```vue
<script setup lang="ts">
import { computed, onMounted, ref, type Component } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import {
  Activity,
  ChevronDown,
  FileText,
  Gauge,
  Headset,
  List,
  Monitor,
  ShoppingCart,
  User,
  UserPlus
} from 'lucide-vue-next'
import { portalRoutes } from '@/router/portal'
import { fetchPortalMe } from '@/api/portal'
import type { PortalUser } from '@/api/portal/types'
import { removeUserToken } from '@/utils/userAuth'
import LanguageSwitch from '@/components/LanguageSwitch/index.vue'
import { getDocById } from '@/views/portal/Docs/articles'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger
} from '@/components/ui/dropdown-menu'
import { cn } from '@/lib/utils'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()

const user = ref<PortalUser | null>(null)

const iconMap: Record<string, Component> = {
  Gauge,
  FileText,
  ShoppingCart,
  Monitor,
  List,
  UserPlus,
  User,
  Headset,
  Activity
}

const menuChildren = computed(() => {
  const portalRoot = portalRoutes.find((r) => r.path === '/portal')
  return portalRoot?.children ?? []
})

interface MenuGroup {
  label?: string
  items: typeof menuChildren.value
}

const menuGroups = computed<MenuGroup[]>(() => {
  const groups: MenuGroup[] = []
  let current: MenuGroup = { items: [] }

  for (const item of menuChildren.value) {
    if (item.meta?.hideInMenu) continue
    const group = item.meta?.group as string | undefined
    if (group) {
      if (current.label !== group) {
        if (current.items.length) groups.push(current)
        current = { label: group, items: [] }
      }
      current.items.push(item)
    } else {
      if (current.label) {
        groups.push(current)
        current = { items: [] }
      }
      current.items.push(item)
    }
  }
  if (current.items.length) groups.push(current)
  return groups
})

const activeMenu = computed(() => {
  if (String(route.name).startsWith('portal-docs')) return 'portal-docs'
  if (String(route.name).startsWith('portal-buy')) return 'portal-buy'
  if (String(route.name).startsWith('portal-order')) return 'portal-orders'
  return route.name as string
})

const pageTitle = computed(() => {
  if (route.name === 'portal-docs-detail') {
    const article = getDocById(String(route.params.id || ''))
    if (article) {
      return t('portal.docs.headerTitle', {
        title: t(article.titleKey),
        date: article.updatedAt
      })
    }
  }
  if (route.name === 'portal-buy-configure') {
    return t('portal.buy.configureTitle')
  }
  if (route.name === 'portal-order-detail') {
    return t('portal.buy.orderDetailTitle')
  }
  const current = menuChildren.value.find((item) => item.name === route.name)
  return current?.meta?.title ? t(current.meta.title as string) : t('portal.menu.dashboard')
})

onMounted(async () => {
  try {
    user.value = await fetchPortalMe()
  } catch {
    /* 401 handled by axios */
  }
})

function onSelect(name: string) {
  router.push({ name })
}

function logout() {
  removeUserToken()
  router.push({ name: 'site-home' })
}
</script>

<template>
  <div class="flex min-h-screen flex-col bg-muted/40">
    <header
      class="grid h-14 shrink-0 items-center border-b border-border bg-card px-5 grid-cols-[1fr_auto_1fr]"
    >
      <div class="text-lg font-bold tracking-tight text-foreground">
        {{ t('portal.siteName') }}
      </div>
      <div class="text-sm font-medium text-muted-foreground">{{ pageTitle }}</div>
      <div class="flex items-center justify-end gap-3">
        <LanguageSwitch />
        <DropdownMenu>
          <DropdownMenuTrigger as-child>
            <Button variant="ghost" class="gap-1.5 text-foreground">
              <User class="size-4" />
              <span class="max-w-40 truncate">{{ user?.email || '...' }}</span>
              <ChevronDown class="size-4 opacity-60" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" class="min-w-40">
            <DropdownMenuItem @click="logout">{{ t('portal.logout') }}</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>

    <div class="flex min-h-0 flex-1 overflow-hidden">
      <aside class="w-55 shrink-0 overflow-auto border-e border-border bg-card">
        <nav class="flex flex-col gap-1 p-3">
          <template v-for="(group, gi) in menuGroups" :key="gi">
            <div
              v-if="group.label"
              class="px-3 pb-1 pt-3 text-xs font-medium text-muted-foreground"
            >
              {{ t(group.label) }}
            </div>
            <button
              v-for="item in group.items"
              :key="item.name as string"
              type="button"
              :class="
                cn(
                  'flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm transition-colors',
                  activeMenu === item.name
                    ? 'bg-primary/10 font-medium text-primary'
                    : 'text-foreground hover:bg-muted'
                )
              "
              @click="onSelect(item.name as string)"
            >
              <component
                :is="iconMap[item.meta!.icon as string] || User"
                class="size-4 shrink-0"
              />
              <span>{{ t(item.meta!.title as string) }}</span>
            </button>
          </template>
        </nav>
      </aside>

      <main class="flex-1 overflow-auto p-6">
        <router-view />
      </main>
    </div>
  </div>
</template>
```

注意：若 Tailwind 无 `w-55`，改用 `w-[220px]`。

- [ ] **Step 3: 验收**

```bash
npm run ts:check
npm run lint
npm run build
```

手动：登录后打开 `/portal/dashboard`，确认顶栏白底、侧栏当前项紫高亮、用户菜单可登出、Buy 页仍正常嵌入壳内。

- [ ] **Step 4: Commit**

```bash
git add src/layout/UserLayout/index.vue src/router/portal.ts
git commit -m "refactor(dashboard): restyle portal UserLayout to SaaS shell"
```

---

### Task 3: 登录页

**Files:**
- Modify: `darknight/dashboard/src/views/auth/Login/index.vue`（整文件）

**Interfaces:**
- Consumes: `Button`、`Input`、`Label`、`Alert`、`Card`（及 CardHeader/Title/Content 若需要）、`loginAccount`、token helpers
- Produces: 无 Element 的登录页；行为与现网一致（admin/user 分流、redirect）

- [ ] **Step 1: 重写 Login**

保留 `resolveRedirect`、`onSubmit` 成功后的 token 逻辑。去掉 `el-form` / `FormRules`，改为本地校验：

```ts
const fieldErrors = reactive({ username: '', password: '' })

function validate(): boolean {
  fieldErrors.username = form.username.trim() ? '' : t('login.fieldRequired')
  fieldErrors.password = form.password ? '' : t('login.fieldRequired')
  return !fieldErrors.username && !fieldErrors.password
}
```

模板结构：

```vue
<template>
  <div class="flex min-h-screen flex-col bg-muted/40 p-6">
    <div class="flex justify-end">
      <LanguageSwitch />
    </div>
    <div class="flex flex-1 items-center justify-center">
      <div class="w-full max-w-sm rounded-xl border border-border bg-card p-7 shadow-sm">
        <div class="mb-3 flex justify-center">
          <img src="/statics/logo.png" alt="DarKnight VPN" class="size-28 rounded-2xl object-contain" />
        </div>
        <h1 class="text-center text-lg font-semibold text-foreground">
          {{ t('login.loginYourAccount') }}
        </h1>
        <p class="mb-5 text-center text-sm text-muted-foreground">
          {{ t('login.welcomeBack') }}
        </p>
        <form class="flex flex-col gap-4" @submit.prevent="onSubmit">
          <div class="space-y-2">
            <Label for="login-username">{{ t('login.accountPlaceholder') }}</Label>
            <Input
              id="login-username"
              v-model="form.username"
              :placeholder="t('login.accountPlaceholder')"
              autocomplete="username"
            />
            <p v-if="fieldErrors.username" class="text-sm text-destructive">
              {{ fieldErrors.username }}
            </p>
          </div>
          <div class="space-y-2">
            <Label for="login-password">{{ t('password') }}</Label>
            <Input
              id="login-password"
              v-model="form.password"
              type="password"
              :placeholder="t('password')"
              autocomplete="current-password"
            />
            <p v-if="fieldErrors.password" class="text-sm text-destructive">
              {{ fieldErrors.password }}
            </p>
          </div>
          <Alert v-if="errorMsg" variant="destructive">
            <AlertDescription>{{ errorMsg }}</AlertDescription>
          </Alert>
          <Button type="submit" class="h-11 w-full" :disabled="loading">
            {{ t('login') }}
          </Button>
        </form>
        <div class="mt-4 text-center">
          <Button variant="link" class="h-auto p-0" @click="goRegister">
            {{ t('portal.goRegister') }}
          </Button>
        </div>
      </div>
    </div>
  </div>
</template>
```

`onSubmit` 开头调用 `if (!validate()) return`。删除全部 scoped 中的 `#20a397` 样式块。

- [ ] **Step 2: 验收**

```bash
npm run ts:check
npm run lint
npm run build
```

手动：空提交显示必填；错误账号显示 Alert；用户登录进 dashboard，admin 进 admin。

- [ ] **Step 3: Commit**

```bash
git add src/views/auth/Login/index.vue
git commit -m "refactor(dashboard): restyle login page with shadcn"
```

---

### Task 4: 注册页 + 滑块验证码

**Files:**
- Modify: `darknight/dashboard/src/views/portal/Register/index.vue`
- Modify: `darknight/dashboard/src/views/portal/Register/components/SlideCaptchaDialog.vue`

**Interfaces:**
- Consumes: Button/Input/Label/Alert、`toast` from `vue-sonner`、`SlideCaptchaDialog`、现有 API
- Produces: 无 Element 表单的注册页；验证码对话框用 AlertDialog 或同风格自定义面板，颜色用 primary token

- [ ] **Step 1: 重写 Register 表单 UI**

布局对齐登录（`bg-muted/40` + 居中 `rounded-xl border bg-card`）。保留：

- autofill trap
- `codeReadonly` / `passwordReadonly` / `confirmReadonly` 与 `unlockField` / `sanitizeCodeInput` / `purgeAutofillNoise`
- 倒计时与 `onSendCode` → 打开 captcha → `onCaptchaSuccess` 发码
- 邀请码可选

校验改为本地函数（email 格式、密码 ≥6、确认一致），不再用 `FormInstance`/`FormRules`。

`ElMessage.success/error` 全部改为：

```ts
import { toast } from 'vue-sonner'
toast.success(...)
toast.error(...)
```

验证码行：

```vue
<div class="flex gap-2">
  <Input class="flex-1" ... />
  <Button type="button" class="shrink-0" :disabled="sending || countdown > 0" @click="onSendCode">
    {{ countdown > 0 ? `${countdown}s` : t('portal.sendCode') }}
  </Button>
</div>
```

- [ ] **Step 2: 重写 SlideCaptchaDialog 外壳**

用已有 `AlertDialog` 替换 `el-dialog`：

```vue
<AlertDialog :open="visible" @update:open="(v) => (visible = v)">
  <AlertDialogContent class="sm:max-w-sm">
    <AlertDialogHeader>
      <AlertDialogTitle>{{ t('portal.slideCaptchaTitle') }}</AlertDialogTitle>
      <AlertDialogDescription>{{ t('portal.slideCaptchaHint') }}</AlertDialogDescription>
    </AlertDialogHeader>
    <!-- 保留 track / handle 交互逻辑 -->
  </AlertDialogContent>
</AlertDialog>
```

若 `visible` computed setter 与 AlertDialog `open` 绑定不便，用：

```vue
<AlertDialog
  :open="props.modelValue"
  @update:open="(v: boolean) => emit('update:modelValue', v)"
>
```

并把 `@closed` 逻辑放到 `watch(() => props.modelValue)` 在关闭时 `reset()`。

进度条/把手颜色改为 token：

- progress：`bg-primary/20`，成功 `bg-primary/35`
- handle：`text-primary border-border bg-card`
- 成功文案：`text-primary`
- 轨道：`bg-muted`
- 禁止 `#20a397` 与物理 `left`（用 `start-0`）

- [ ] **Step 3: 验收**

```bash
npm run ts:check
npm run lint
npm run build
```

手动：发码弹出滑块、拖过成功后倒计时、注册成功进 dashboard。

- [ ] **Step 4: Commit**

```bash
git add src/views/portal/Register/index.vue src/views/portal/Register/components/SlideCaptchaDialog.vue
git commit -m "refactor(dashboard): restyle register and slide captcha"
```

---

### Task 5: 仪表盘

**Files:**
- Modify: `darknight/dashboard/src/views/portal/Dashboard/index.vue`（整文件）

**Interfaces:**
- Consumes: Card/Badge/Button/Input、lucide、`fetchPortalMe`、`formatBytes`
- Produces: 公告白卡 + 订阅/快捷入口双列；无青绿渐变

- [ ] **Step 1: 重写 Dashboard**

shortcuts 的 icon 改为 lucide：`BookOpen`、`Link2`、`ShoppingCart`、`LifeBuoy`。

模板要点：

```vue
<div class="flex max-w-6xl flex-col gap-4">
  <div class="rounded-xl border border-border bg-card p-5">
    <Badge variant="secondary">{{ t('portal.dashboard.announcement') }}</Badge>
    <p class="mt-3 text-sm text-foreground">{{ t('portal.dashboard.announcementText') }}</p>
    <p class="mt-2 text-xs text-muted-foreground">2026-08-19</p>
  </div>

  <div class="grid gap-4 md:grid-cols-2">
    <div class="rounded-xl border border-border bg-card p-5">
      <h2 class="mb-4 text-base font-semibold">{{ t('portal.dashboard.mySubscription') }}</h2>
      <!-- 有订阅：状态/流量 + Input readonly + Button 复制 -->
      <!-- 无订阅：dashed border 区域点击去 buy，lucide Plus -->
    </div>
    <div class="rounded-xl border border-border bg-card p-5">
      <h2 class="mb-2 text-base font-semibold">{{ t('portal.dashboard.shortcuts') }}</h2>
      <!-- 每项 flex justify-between，border-b border-border，最后一项无边框 -->
    </div>
  </div>
</div>
```

空订阅区：

```vue
<button
  type="button"
  class="flex min-h-44 w-full flex-col items-center justify-center gap-2 rounded-lg border border-dashed border-border text-muted-foreground hover:bg-muted/50"
  @click="router.push({ name: 'portal-buy' })"
>
  <Plus class="size-10" />
  <span>{{ t('portal.dashboard.buySubscription') }}</span>
</button>
```

删除所有 scoped 硬编码色与 `el-*`。

- [ ] **Step 2: 验收**

```bash
npm run ts:check
npm run lint
npm run build
```

手动：有/无订阅两种态；快捷入口跳转；窄屏单列。

- [ ] **Step 3: Commit**

```bash
git add src/views/portal/Dashboard/index.vue
git commit -m "refactor(dashboard): restyle portal dashboard cards"
```

---

### Task 6: 文档列表 + 详情

**Files:**
- Modify: `darknight/dashboard/src/views/portal/Docs/index.vue`
- Modify: `darknight/dashboard/src/views/portal/Docs/Detail.vue`

**Interfaces:**
- Consumes: Input、Button、Card、`toast`、lucide `Search`/`Download`、articles helpers
- Produces: 无 `#20a397` 的文档列表与详情

- [ ] **Step 1: 重写 Docs/index.vue**

```vue
<template>
  <div class="max-w-3xl rounded-xl border border-border bg-card p-6">
    <div class="relative mb-6">
      <Search class="pointer-events-none absolute start-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
      <Input v-model="keyword" class="ps-9" :placeholder="t('portal.docs.search')" />
    </div>
    <p v-if="!groups.length" class="py-10 text-center text-sm text-muted-foreground">
      {{ t('portal.docs.emptySearch') }}
    </p>
    <section v-for="group in groups" :key="group.id" class="mb-6 last:mb-0">
      <h2 class="mb-2 text-base font-semibold text-foreground">{{ t(group.titleKey) }}</h2>
      <button
        v-for="article in group.articles"
        :key="article.id"
        type="button"
        class="flex w-full items-center justify-between gap-4 rounded-lg px-3 py-3 text-start hover:bg-muted"
        @click="openArticle(article.id)"
      >
        <span class="font-medium text-foreground">{{ t(article.titleKey) }}</span>
        <span class="shrink-0 text-sm text-muted-foreground">{{ article.updatedAt }}</span>
      </button>
    </section>
  </div>
</template>
```

- [ ] **Step 2: 重写 Docs/Detail.vue**

- `ElMessage` → `toast.warning` / `toast.success`
- 外层：`max-w-3xl rounded-xl border border-border bg-card p-6 text-foreground`
- lead / step title：`font-bold`
- paragraph / step body：`text-muted-foreground`
- downloads：`Button` 全宽或 `a` 带 `buttonVariants({ class: 'w-full' })` + `Download` lucide；`bg-primary text-primary-foreground`
- note：`rounded-lg bg-muted p-4 text-sm text-muted-foreground`
- copySub / importClash / importShadowrocket：`<Button class="mt-2 w-full" @click="...">`

删除 scoped 中所有青绿与灰硬编码。

- [ ] **Step 3: 验收**

```bash
npm run ts:check
npm run lint
npm run build
```

手动：搜索过滤、打开详情、复制订阅（无订阅时 toast 警告）。

- [ ] **Step 4: Commit**

```bash
git add src/views/portal/Docs/index.vue src/views/portal/Docs/Detail.vue
git commit -m "refactor(dashboard): restyle portal docs list and detail"
```

---

### Task 7: 订单列表

**Files:**
- Modify: `darknight/dashboard/src/views/portal/Orders/index.vue`（整文件）

**Interfaces:**
- Consumes: Alert、Badge、Button、Skeleton、现有 `fetchPortalOrders` / plans helpers
- Produces: 白卡表格列表，无 `el-table`

- [ ] **Step 1: 重写 Orders/index.vue**

状态映射改为 Badge variant：

```ts
const STATUS_VARIANT: Record<OrderStatus, 'secondary' | 'default' | 'outline' | 'destructive'> = {
  pending: 'secondary',
  paid: 'default',
  closed: 'outline',
  failed: 'destructive'
}
```

加载态：3–5 行 `Skeleton`。

错误：顶部 `Alert variant="destructive"`。

表格用语义化 HTML（注意 RTL：表头 `text-start`）：

```vue
<div class="max-w-6xl">
  <Alert v-if="isError" variant="destructive" class="mb-4">...</Alert>

  <div class="overflow-x-auto rounded-xl border border-border bg-card">
    <div v-if="isLoading" class="space-y-3 p-4">
      <Skeleton v-for="i in 5" :key="i" class="h-10 w-full" />
    </div>
    <template v-else-if="!(data ?? []).length">
      <div class="flex flex-col items-center gap-3 py-10 text-muted-foreground">
        <p>{{ t('portal.orders.empty') }}</p>
        <Button @click="router.push({ name: 'portal-buy' })">
          {{ t('portal.buy.subscribeNow') }}
        </Button>
      </div>
    </template>
    <table v-else class="w-full min-w-[720px] text-sm">
      <thead class="border-b border-border text-muted-foreground">
        <tr>
          <th class="px-4 py-3 text-start font-medium">{{ t('portal.buy.orderNo') }}</th>
          <th class="px-4 py-3 text-start font-medium">{{ t('portal.buy.productInfo') }}</th>
          <th class="px-4 py-3 text-start font-medium">{{ t('portal.buy.orderTotal') }}</th>
          <th class="px-4 py-3 text-start font-medium">{{ t('portal.orders.status') }}</th>
          <th class="px-4 py-3 text-start font-medium">{{ t('portal.buy.createdAt') }}</th>
          <th class="px-4 py-3 text-end font-medium">{{ t('portal.orders.action') }}</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="row in data"
          :key="row.id"
          class="border-b border-border last:border-0"
        >
          <td class="px-4 py-3">
            <button type="button" class="text-primary hover:underline" @click="openOrder(row)">
              {{ row.id }}
            </button>
          </td>
          <td class="px-4 py-3">
            {{ planName(row) }} · {{ t(getCycleLabelKey(row.cycle_id)) }}
          </td>
          <td class="px-4 py-3">
            {{ currencySymbol(row.currency) }}{{ formatPrice(row.amount) }}
          </td>
          <td class="px-4 py-3">
            <Badge :variant="STATUS_VARIANT[row.status]">
              {{ t(`portal.orders.status.${row.status}`) }}
            </Badge>
          </td>
          <td class="px-4 py-3 text-muted-foreground">{{ formatOrderTime(row.created_at) }}</td>
          <td class="px-4 py-3 text-end">
            <Button
              size="sm"
              :variant="row.status === 'pending' ? 'default' : 'outline'"
              @click="openOrder(row)"
            >
              {{
                row.status === 'pending'
                  ? t('portal.buy.checkout')
                  : t('portal.orders.detail')
              }}
            </Button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</div>
```

保留 `useQuery` 与 `openOrder` 行为。

- [ ] **Step 2: 全量回归验收**

```bash
npm run ts:check
npm run lint
npm run build
```

手动清单（对照 spec 验收）：

- [ ] 门户壳无青绿顶栏；当前菜单紫高亮  
- [ ] 登录/注册/仪表盘/文档/订单列表无 `#20a397`；主 CTA 为 primary  
- [ ] 仪表盘窄屏单列  
- [ ] 登录跳转、注册验证码、复制订阅、打开订单详情正常  
- [ ] `/portal/buy` 与订单详情观感未被破坏  

在触及文件中搜索硬编码色，应无匹配：

```bash
rg "#20a397|#1b8c82|#eef2f6|#f5f7fa" src/layout/UserLayout src/views/auth/Login src/views/portal/Register src/views/portal/Dashboard src/views/portal/Docs src/views/portal/Orders/index.vue
```

Expected：无输出。

- [ ] **Step 3: Commit**

```bash
git add src/views/portal/Orders/index.vue
git commit -m "refactor(dashboard): restyle portal orders list with shadcn"
```

---

## Spec Coverage Checklist

| Spec 项 | Task |
|---------|------|
| UserLayout 白顶栏/紫侧栏 | Task 2 |
| DropdownMenu | Task 1–2 |
| lucide 侧栏图标 | Task 2 |
| 登录 | Task 3 |
| 注册 + 滑块外层 | Task 4 |
| 仪表盘 | Task 5 |
| 文档列表/详情 | Task 6 |
| 订单列表 | Task 7 |
| 不做官网/Admin/占位/卸 Element | 全局约束 |
| 验收标准 | Task 7 Step 2 |

## Self-Review Notes

- 无 TBD/占位步骤；表单校验策略在 Task 3/4 写明为本地函数。
- `PortalPage` 封装按 YAGNI 未单独立项（各页自带 `max-w-*`）。
- `LanguageSwitch` 明确本批可保留 Element，避免与「不做 Admin」冲突。
