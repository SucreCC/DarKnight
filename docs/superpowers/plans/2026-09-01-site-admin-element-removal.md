# 官网 + Admin + 卸载 Element Plus Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把官网、门户占位页、Admin 壳与全部业务页迁到与门户一致的 Tailwind + shadcn 风格，并卸载 Element Plus。

**Architecture:** 按区推进：官网/占位 → 共享组件 → Admin 壳 → Setting/Node/Host/User → 全仓扫残留并卸载 Element。确认框统一用已有 `useConfirm()` + `ConfirmDialog`；提示用 `toast`（vue-sonner）。大表单用 shadcn Dialog；开关/选择按需补 Switch、Select。

**Tech Stack:** Vue 3.5、Vite、TypeScript、Tailwind CSS v4、shadcn-vue（Reka UI）、lucide-vue-next、vue-sonner、vue-i18n 10、@tanstack/vue-query 5

**Spec:** `docs/superpowers/specs/2026-09-01-site-admin-element-removal-design.md`

## Global Constraints

- 所有命令在 `e:\kai\DarKnight\darknight\dashboard` 下执行，包管理器用 `npm`。
- 设计令牌沿用 `src/assets/css/globals.css`；主色亮色 `oklch(0.585 0.233 277.1)`，暗色 `oklch(0.66 0.19 277.1)`。
- 本计划触及的文件内不得残留写死颜色（`#20a397`、`#1b8c82`、`#1b8f84`、`#303133`、`#606266`、`#909399`、`#dcdfe6`、`#e4e7ed`、`#f5f7fa`、`#eef2f6`），一律改用令牌类。
- 间距/定位用逻辑属性（`ms-`/`me-`/`ps-`/`pe-`/`start-`/`end-`/`text-start`/`text-end`），禁止物理方向类；支持 RTL。
- 不改后端、路由 name、业务 API、store 行为；只换 UI。
- 不做：官网新营销内容、占位页真实功能、新 Admin 功能、引入重型 table 库。
- 确认：`import { useConfirm } from '@/composables/useConfirm'` → `await confirm({ title, description, destructive?: true })`（取消会 reject）。
- 提示：`import { toast } from 'vue-sonner'`；禁止新增 `ElMessage` / `ElMessageBox`。
- 无测试框架；验收 = `npm run ts:check` + `npm run lint` + `npm run build`（Element 卸完后 ts:check 必须无错；卸之前允许既有 PayPal Timeout 误报继续存在）。
- i18n 扁平点号键；尽量不新增 key；若必须新增，同时写 `zh.json`、`en.json`、`ru.json`、`fa.json`。
- 每任务结束提交一次；英文信息：`feat(dashboard): ...` / `refactor(dashboard): ...` / `chore(dashboard): ...`。

## File Map

| 区域 | 文件 |
|------|------|
| 官网 | `src/layout/SiteLayout/index.vue`、`src/views/site/Home/index.vue` |
| 占位 | `src/views/portal/Placeholder/index.vue` |
| 共享 | `src/components/LanguageSwitch/index.vue`、`src/components/ThemeToggle/index.vue` |
| UI 基建 | `src/components/ui/dialog/*`、`switch/*`、`select/*`（CLI 生成） |
| Admin 壳 | `src/layout/index.vue`、`Menu`、`ToolHeader`、`Breadcrumb`、`TagsView`、`Setting`、`src/router/admin.ts` |
| Setting 页 | `src/views/admin/Setting/index.vue` |
| Node | `src/views/admin/Node/index.vue`、`NodesTable.vue`、`NodeDialog.vue` |
| Host | `src/views/admin/Host/index.vue`、`HostForm.vue` |
| User | `src/views/admin/User/index.vue` + `UserFilters`/`UsersTable`/`UserDialog`/`QRCodeDialog`/`Statistics` + 可选 `api/user/types.ts` 状态映射 |
| 卸载 | `src/main.ts`、`src/App.vue`、`build/vite/index.ts`、`build/vite/optimize.ts`、`package.json`、`tsconfig.json`、生成的 `types/auto-*.d.ts` |

---

### Task 1: 补齐 Dialog / Switch / Select

**Files:**
- Create: `src/components/ui/dialog/*`、`switch/*`、`select/*`

**Interfaces:**
- Consumes: 现有 `components.json`、`reka-ui`
- Produces: 可从 `@/components/ui/dialog`、`@/components/ui/switch`、`@/components/ui/select` 导入标准 shadcn 导出

- [ ] **Step 1: CLI 添加组件**

```bash
cd darknight/dashboard
npx shadcn-vue@latest add dialog switch select --yes
```

Expected：三个目录各有 `index.ts`。

- [ ] **Step 2: 确认导出**

打开各 `index.ts`，记下实际导出名（后续任务按实际名 import）。至少需要：

- Dialog: `Dialog`、`DialogContent`、`DialogHeader`、`DialogTitle`、`DialogFooter`、`DialogDescription`
- Switch: `Switch`
- Select: `Select`、`SelectTrigger`、`SelectValue`、`SelectContent`、`SelectItem`

- [ ] **Step 3: Commit**

```bash
git add src/components/ui/dialog src/components/ui/switch src/components/ui/select package.json package-lock.json
git commit -m "feat(dashboard): add shadcn dialog, switch, and select"
```

---

### Task 2: 官网 SiteLayout + Home

**Files:**
- Modify: `src/layout/SiteLayout/index.vue`（整文件）
- Modify: `src/views/site/Home/index.vue`（整文件）

**Interfaces:**
- Consumes: Button、LanguageSwitch（仍可暂时 Element，Task 3 再换）、lucide
- Produces: 无 `#20a397` 的官网

- [ ] **Step 1: 重写 SiteLayout**

```vue
<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import LanguageSwitch from '@/components/LanguageSwitch/index.vue'
import { Button } from '@/components/ui/button'

const { t } = useI18n()
const router = useRouter()
</script>

<template>
  <div class="flex min-h-screen flex-col bg-muted/40">
    <header class="border-b border-border bg-card">
      <div
        class="mx-auto flex h-16 max-w-5xl items-center justify-between gap-6 px-6"
      >
        <button
          type="button"
          class="inline-flex items-center gap-2.5 border-0 bg-transparent p-0 text-xl font-bold text-foreground"
          @click="router.push({ name: 'site-home' })"
        >
          <img
            src="/statics/logo.png"
            alt="DarKnight"
            class="size-8 rounded-lg object-contain"
          />
          <span>DarKnight</span>
        </button>
        <div class="flex items-center gap-3">
          <LanguageSwitch />
          <Button variant="outline" @click="router.push({ name: 'login' })">
            {{ t('portal.login') }}
          </Button>
          <Button @click="router.push({ name: 'portal-register' })">
            {{ t('portal.register') }}
          </Button>
        </div>
      </div>
    </header>
    <main class="mx-auto w-full max-w-5xl flex-1 px-6 py-8">
      <router-view />
    </main>
    <footer
      class="border-t border-border bg-card px-6 py-5 text-center text-[13px] text-muted-foreground"
    >
      {{ t('site.footer') }}
    </footer>
  </div>
</template>
```

- [ ] **Step 2: 重写 Home**

```vue
<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Cable, FileText, Lock } from 'lucide-vue-next'
import type { Component } from 'vue'
import { Button } from '@/components/ui/button'

const { t } = useI18n()
const router = useRouter()

const features: { icon: Component; title: string; desc: string }[] = [
  { icon: Lock, title: 'site.home.feature1Title', desc: 'site.home.feature1Desc' },
  { icon: Cable, title: 'site.home.feature2Title', desc: 'site.home.feature2Desc' },
  { icon: FileText, title: 'site.home.feature3Title', desc: 'site.home.feature3Desc' }
]
</script>

<template>
  <section class="flex flex-col gap-8">
    <div
      class="rounded-2xl bg-primary px-6 py-12 text-center text-primary-foreground sm:px-10 sm:py-14"
    >
      <h1 class="m-0 text-3xl font-bold sm:text-4xl">{{ t('site.home.title') }}</h1>
      <p class="mx-auto mb-7 mt-4 max-w-xl text-base leading-relaxed opacity-90">
        {{ t('site.home.subtitle') }}
      </p>
      <div class="flex flex-col items-center justify-center gap-3 sm:flex-row">
        <Button
          class="h-11 bg-primary-foreground text-primary hover:bg-primary-foreground/90"
          @click="router.push({ name: 'portal-register' })"
        >
          {{ t('site.home.getStarted') }}
        </Button>
        <Button
          variant="outline"
          class="h-11 border-primary-foreground/40 bg-transparent text-primary-foreground hover:bg-primary-foreground/10"
          @click="router.push({ name: 'login' })"
        >
          {{ t('site.home.login') }}
        </Button>
      </div>
    </div>

    <div class="grid gap-5 md:grid-cols-3">
      <div
        v-for="item in features"
        :key="item.title"
        class="min-h-44 rounded-xl border border-border bg-card p-6"
      >
        <component :is="item.icon" class="mb-3 size-7 text-primary" />
        <h3 class="mb-2 text-lg font-semibold text-foreground">{{ t(item.title) }}</h3>
        <p class="m-0 text-sm leading-relaxed text-muted-foreground">{{ t(item.desc) }}</p>
      </div>
    </div>
  </section>
</template>
```

- [ ] **Step 3: 验收**

```bash
npm run build
rg "#20a397|#17867c" src/layout/SiteLayout src/views/site/Home
```

Expected：build 通过；rg 无输出。

- [ ] **Step 4: Commit**

```bash
git add src/layout/SiteLayout/index.vue src/views/site/Home/index.vue
git commit -m "refactor(dashboard): restyle site layout and home page"
```

---

### Task 3: 占位页 + LanguageSwitch + ThemeToggle

**Files:**
- Modify: `src/views/portal/Placeholder/index.vue`
- Modify: `src/components/LanguageSwitch/index.vue`
- Modify: `src/components/ThemeToggle/index.vue`

**Interfaces:**
- Consumes: DropdownMenu（已有）、Button、lucide
- Produces: 三处不再依赖 Element

- [ ] **Step 1: Placeholder**

```vue
<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'

const { t } = useI18n()
const route = useRoute()
</script>

<template>
  <div
    class="flex min-h-80 flex-col items-center justify-center gap-2 rounded-xl border border-border bg-card p-8 text-center"
  >
    <p class="font-medium text-foreground">{{ t(route.meta.title as string) }}</p>
    <p class="text-sm text-muted-foreground">{{ t('portal.comingSoon') }}</p>
  </div>
</template>
```

- [ ] **Step 2: LanguageSwitch（DropdownMenu）**

```vue
<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { ChevronDown } from 'lucide-vue-next'
import { SUPPORTED_LOCALES, setLocale, type LocaleCode } from '@/plugins/vueI18n'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger
} from '@/components/ui/dropdown-menu'

const { locale } = useI18n()

const currentLabel = () =>
  SUPPORTED_LOCALES.find((item) => item.value === locale.value)?.label ?? locale.value

function onChange(value: LocaleCode) {
  setLocale(value)
}
</script>

<template>
  <DropdownMenu>
    <DropdownMenuTrigger as-child>
      <Button variant="outline" class="min-w-30 justify-between gap-2">
        <span>{{ currentLabel() }}</span>
        <ChevronDown class="size-4 opacity-60" />
      </Button>
    </DropdownMenuTrigger>
    <DropdownMenuContent align="end" class="min-w-30">
      <DropdownMenuItem
        v-for="item in SUPPORTED_LOCALES"
        :key="item.value"
        @click="onChange(item.value)"
      >
        {{ item.label }}
      </DropdownMenuItem>
    </DropdownMenuContent>
  </DropdownMenu>
</template>
```

若 `min-w-30` 无效，改用 `min-w-[7.5rem]`。

- [ ] **Step 3: ThemeToggle**

```vue
<script setup lang="ts">
import { computed } from 'vue'
import { Moon, Sun } from 'lucide-vue-next'
import { useThemeStore } from '@/store/modules/theme'
import { Button } from '@/components/ui/button'

const theme = useThemeStore()
const isDark = computed(() => theme.mode === 'dark')
</script>

<template>
  <Button variant="ghost" size="icon" type="button" @click="theme.toggle()">
    <Moon v-if="isDark" class="size-4" />
    <Sun v-else class="size-4" />
  </Button>
</template>
```

- [ ] **Step 4: 验收 + Commit**

```bash
npm run build
git add src/views/portal/Placeholder/index.vue src/components/LanguageSwitch/index.vue src/components/ThemeToggle/index.vue
git commit -m "refactor(dashboard): restyle placeholder and shared locale/theme controls"
```

---

### Task 4: Admin 壳（layout + 子组件 + 路由图标）

**Files:**
- Modify: `src/router/admin.ts`（icon 字符串）
- Modify: `src/layout/index.vue`
- Modify: `src/layout/components/Menu/index.vue`
- Modify: `src/layout/components/ToolHeader/index.vue`
- Modify: `src/layout/components/Breadcrumb/index.vue`
- Modify: `src/layout/components/TagsView/index.vue`
- Modify: `src/layout/components/Setting/index.vue`

**Interfaces:**
- Consumes: DropdownMenu、Button、Switch、lucide、`useAppStore`、`useTagsViewStore`
- Produces: 无 Element 的 Admin 壳；`meta.icon` 为 lucide 名

- [ ] **Step 1: 更新 admin 路由 icon**

| name | 新 icon |
|------|---------|
| users | `Users` |
| nodes | `Network` |
| hosts | `Link` |
| settings | `Settings` |

- [ ] **Step 2: 重写 `layout/index.vue` 样式层**

保留 script 与结构；scoped 样式改为 Tailwind class：

```vue
<template>
  <div class="flex h-screen w-full overflow-hidden">
    <aside
      class="flex shrink-0 flex-col overflow-hidden border-e border-border bg-card transition-[width,flex-basis] duration-200"
      :style="{ width: asideWidth, flexBasis: asideWidth }"
    >
      <Menu />
    </aside>
    <div class="flex min-w-0 flex-1 flex-col overflow-hidden">
      <ToolHeader @open-setting="settingVisible = true" />
      <TagsView v-if="appStore.showTagsView" />
      <main class="flex-1 overflow-auto bg-muted/40 p-4">
        <router-view />
      </main>
    </div>
  </div>
  <Setting v-model="settingVisible" />
</template>
```

删除依赖 `--el-*` 的 scoped CSS。

- [ ] **Step 3: Menu — 对齐 UserLayout 侧栏模式**

- 去掉 `el-menu` / Element icons
- `iconMap`：`Users`、`Network`、`Link`、`Settings` from lucide
- 折叠：`appStore.collapsed` 时隐藏文字、缩窄 padding
- 当前项：`bg-primary/10 text-primary`
- 品牌区保留 logo + 条件显示文字

- [ ] **Step 4: ToolHeader**

- 折叠按钮、设置按钮：`Button variant="ghost" size="icon"` + lucide `PanelLeft` / `Settings`
- 用户菜单：DropdownMenu（同门户）
- 保留 `LanguageSwitch`、`ThemeToggle`、`Breadcrumb`、logout 逻辑

- [ ] **Step 5: Breadcrumb**

读现有逻辑，改为：

```vue
<nav class="flex items-center gap-2 text-sm text-muted-foreground">
  <!-- 按现有 items 循环，当前页 text-foreground -->
</nav>
```

不要 `el-breadcrumb`。

- [ ] **Step 6: TagsView**

保留 tags store 的增删/点击行为。UI：

```vue
<div class="flex gap-2 overflow-x-auto border-b border-border bg-card px-3 py-2">
  <button
    v-for="tag in ..."
    type="button"
    :class="cn(
      'inline-flex items-center gap-1 rounded-md border px-2.5 py-1 text-xs',
      isActive ? 'border-primary/30 bg-primary/10 text-primary' : 'border-border text-muted-foreground'
    )"
  >
    {{ title }}
    <button type="button" @click.stop="close">×</button>
  </button>
</div>
```

用现有 store API，不要改关闭语义。

- [ ] **Step 7: Setting 侧滑面板**

替换 `el-drawer`：

```vue
<template>
  <div v-if="visible" class="fixed inset-0 z-50">
    <button
      type="button"
      class="absolute inset-0 bg-black/50"
      aria-label="close"
      @click="visible = false"
    />
    <aside
      class="absolute inset-y-0 end-0 flex w-[300px] flex-col gap-4 border-s border-border bg-card p-5 shadow-lg"
    >
      <h2 class="text-base font-semibold">{{ t('layout.settings') }}</h2>
      <div class="flex items-center justify-between py-3">
        <span>{{ t('layout.darkMode') }}</span>
        <Switch v-model="isDark" />
      </div>
      <!-- breadcrumb / tagsView 同理，用 Switch + appStore setters -->
    </aside>
  </div>
</template>
```

若 shadcn `Switch` 的 v-model 是 `checked` 而非 boolean model，按组件实际 props 绑定（常见：`:checked` + `@update:checked`）。

- [ ] **Step 8: 验收 + Commit**

```bash
npm run build
git add src/layout src/router/admin.ts
git commit -m "refactor(dashboard): restyle admin shell without Element"
```

手动：登录 admin，折叠侧栏、切标签、开设置抽屉、登出。

---

### Task 5: Admin Setting 页

**Files:**
- Modify: `src/views/admin/Setting/index.vue`

**Interfaces:**
- Consumes: Button、toast、现有 setting API / websocket
- Produces: 无 Element 的核心配置页

- [ ] **Step 1: UI 替换清单**

| 原 | 新 |
|----|----|
| `ElMessage.*` | `toast.success` / `toast.error` |
| 工具栏 `el-button` | `Button` |
| JSON 编辑区 | `<textarea class="... rounded-lg border border-input bg-background font-mono text-sm">` |
| 日志区容器 | `rounded-xl border bg-card` |

保留：`configText`、`onSave` JSON.parse、`useRestartCore`、日志 WebSocket 逻辑。

- [ ] **Step 2: 验收 + Commit**

```bash
npm run build
git add src/views/admin/Setting/index.vue
git commit -m "refactor(dashboard): restyle admin settings page"
```

---

### Task 6: Admin Node

**Files:**
- Modify: `src/views/admin/Node/index.vue`
- Modify: `src/views/admin/Node/components/NodesTable.vue`
- Modify: `src/views/admin/Node/components/NodeDialog.vue`

**Interfaces:**
- Consumes: table 模式（同 portal Orders）、Dialog、Button、Input、Label、`useConfirm`、toast、lucide
- Produces: 无 Element 的节点页

- [ ] **Step 1: index.vue**

- `ElMessageBox.confirm` →：

```ts
import { useConfirm } from '@/composables/useConfirm'
const { confirm } = useConfirm()

async function onRemove(node: NodeType) {
  try {
    await confirm({
      title: t('deleteNode.title'),
      description: t('deleteNode.prompt', { name: node.name }),
      destructive: true
    })
  } catch {
    return
  }
  if (node.id == null) return
  await deleteNode.mutateAsync(node.id)
  toast.success(t('deleteNode.deleteSuccess', { name: node.name }))
}
```

- `ElMessage` → toast
- 顶部「新建」：`Button` + lucide `Plus`

- [ ] **Step 2: NodesTable**

按 `Orders/index.vue` 模式：白卡 + `<table>` + Skeleton；操作列 Button/ghost icon。去掉 `el-table` / `v-loading`。

- [ ] **Step 3: NodeDialog**

- 外壳：`Dialog` + `DialogContent`（绑定 `modelValue`/`open`）
- 字段：`Input`/`Label`；提交 `Button`
- 校验：去掉 `FormInstance`，改为本地函数
- 成功/失败：toast

- [ ] **Step 4: 验收 + Commit**

```bash
npm run build
git add src/views/admin/Node
git commit -m "refactor(dashboard): restyle admin nodes with shadcn"
```

---

### Task 7: Admin Host

**Files:**
- Modify: `src/views/admin/Host/index.vue`
- Modify: `src/views/admin/Host/components/HostForm.vue`

**Interfaces:**
- Consumes: Button、Input、Label、Switch、Select、toast、lucide `Plus`/`Trash2`
- Produces: 无 Element 的 Host 配置页

- [ ] **Step 1: Host/index.vue**

- 去掉 `el-collapse`：每个 tag 用：

```vue
<details class="mb-4 rounded-xl border border-border bg-card p-4" open>
  <summary class="cursor-pointer font-semibold">{{ tag }}</summary>
  <HostForm v-for="..." ... />
</details>
```

- 保存/添加：`Button`；`ElMessage` → toast

- [ ] **Step 2: HostForm.vue — 字段一一替换**

保留 `defineModel<HostEntry>`。模板结构：

```vue
<div class="rounded-xl border border-border bg-card p-4">
  <div class="mb-4 flex items-center gap-2">
    <Input v-model="host.remark" class="max-w-55" placeholder="Remark" />
    <div class="flex-1" />
    <div class="flex items-center gap-2">
      <span class="text-sm text-muted-foreground">{{ t('status.disabled') }}</span>
      <Switch :checked="host.is_disabled" @update:checked="(v) => (host.is_disabled = v)" />
    </div>
    <Button variant="ghost" size="icon" type="button" @click="$emit('remove')">
      <Trash2 class="size-4 text-destructive" />
    </Button>
  </div>
  <!-- grid of Label+Input / Select for address, port, host, sni, path, security, alpn, fingerprint, ... -->
</div>
```

把原 `el-form-item` 全部改为 `space-y-2` 的 Label+控件；`el-input-number` 用 `Input type="number"`；`el-select` 用 Task 1 的 Select；其余布尔 `Switch`。

选项常量继续从 `@/api/host/types` 导入（`ALPN_OPTIONS` 等）。

- [ ] **Step 3: 验收 + Commit**

```bash
npm run build
git add src/views/admin/Host
git commit -m "refactor(dashboard): restyle admin hosts forms"
```

---

### Task 8: Admin User（Filters + Statistics + Table）

**Files:**
- Modify: `src/views/admin/User/index.vue`
- Modify: `src/views/admin/User/components/UserFilters.vue`
- Modify: `src/views/admin/User/components/Statistics.vue`
- Modify: `src/views/admin/User/components/UsersTable.vue`
- Modify: `src/api/user/types.ts`（可选：增加 Badge variant 映射）

**Interfaces:**
- Consumes: Button、Input、Badge、Skeleton、Select、`useConfirm`、toast
- Produces: 列表区无 Element（Dialog 留 Task 9）

- [ ] **Step 1: index.vue 确认流**

所有 `ElMessageBox.confirm` → `useConfirm().confirm`；所有 `ElMessage` → toast。props/emit 传到子组件保持不变。

- [ ] **Step 2: UserFilters**

搜索/状态下拉/刷新：Input + Select + Button；去掉 `el-form`/`el-select`。

- [ ] **Step 3: Statistics**

统计卡改为：

```vue
<div class="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
  <div class="rounded-xl border border-border bg-card p-4">
    <p class="text-sm text-muted-foreground">...</p>
    <p class="text-2xl font-bold text-foreground">...</p>
  </div>
</div>
```

进度条若有：用 `div` + `bg-primary` 宽度百分比，不用 `el-progress`。

- [ ] **Step 4: UsersTable**

- 语义化 table（列：用户名、状态、用量、到期、操作）
- 状态 Badge：新增映射（可写在组件内）：

```ts
const STATUS_BADGE: Record<string, 'default' | 'secondary' | 'outline' | 'destructive'> = {
  active: 'default',
  connected: 'default',
  disabled: 'secondary',
  expired: 'outline',
  on_hold: 'secondary',
  connecting: 'outline',
  limited: 'destructive',
  error: 'destructive'
}
```

- 分页：底栏「上一页 / 第 n 页 / 下一页」+ 每页条数 Select；继续 `emit('update:page')` / `update:limit`
- 复制：`toast.success` / `toast.error`
- 图标：lucide `Copy`、`Trash2`、`Pencil`、`QrCode`、`Link`
- 加载：Skeleton；去掉 `el-table` / `v-loading`

- [ ] **Step 5: Commit**

```bash
npm run build
git add src/views/admin/User/index.vue src/views/admin/User/components/UserFilters.vue src/views/admin/User/components/Statistics.vue src/views/admin/User/components/UsersTable.vue src/api/user/types.ts
git commit -m "refactor(dashboard): restyle admin users list and filters"
```

---

### Task 9: Admin User Dialogs（UserDialog + QRCodeDialog）

**Files:**
- Modify: `src/views/admin/User/components/UserDialog.vue`
- Modify: `src/views/admin/User/components/QRCodeDialog.vue`

**Interfaces:**
- Consumes: Dialog、Input、Label、Select、Switch、Button、toast、现有 mutations / form model 逻辑
- Produces: 无 Element 的用户编辑与二维码弹窗

- [ ] **Step 1: UserDialog 外壳**

保留现有 `FormModel`、`defaultModel`、watch 填充、create/update 提交逻辑。替换：

- `el-dialog` → `Dialog` `:open="modelValue" @update:open="emit('update:modelValue', $event)"`
- `DialogContent` 加 `class="max-h-[90vh] overflow-y-auto sm:max-w-lg"`
- `FormRules`/`formRef` → `validate(): boolean` 本地校验（username 必填等）
- `ElMessage` → toast
- `el-input`/`el-select`/`el-switch`/`el-checkbox-group` → Input / Select / Switch / 原生 checkbox 组
- 日期：继续用原生 `input type="datetime-local"`（若已有）或等价数字字段 UI，不引日历库

协议多选、inbounds 多选：用 checkbox 列表 + token 样式，不必强上复杂 Select multiple。

- [ ] **Step 2: QRCodeDialog**

- Dialog 外壳同模式
- 保留 `qrcode.vue` 展示
- 关闭/标题用 DialogHeader

- [ ] **Step 3: 验收 + Commit**

```bash
npm run build
git add src/views/admin/User/components/UserDialog.vue src/views/admin/User/components/QRCodeDialog.vue
git commit -m "refactor(dashboard): restyle admin user dialogs with shadcn"
```

手动：新建/编辑用户、删用户确认、二维码、复制订阅。

---

### Task 10: 卸载 Element Plus

**Files:**
- Modify: `src/main.ts`、`src/App.vue`
- Modify: `build/vite/index.ts`、`build/vite/optimize.ts`
- Modify: `package.json`、`tsconfig.json`
- Possibly: `types/auto-components.d.ts`、`types/auto-imports.d.ts`、`.eslintrc-auto-import.json`
- Modify: `src/styles/index.scss`（若仍引用 `--el-*` 则改为 token 或删除）

**Interfaces:**
- Consumes: 前面任务已清零 Element 使用
- Produces: 构建产物不依赖 element-plus

- [ ] **Step 1: 全仓搜索残留**

```bash
rg "element-plus|@element-plus|ElMessage|ElMessageBox|ElConfigProvider|<el-" src
```

Expected：无业务引用。若有，先修再继续（不要跳过）。

- [ ] **Step 2: 改 main.ts**

```ts
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { VueQueryPlugin } from '@tanstack/vue-query'
import '@/assets/css/globals.css'
import '@/styles/index.scss'

import App from '@/App.vue'
import router from '@/router'
import '@/permission'
import { i18n, setLocale } from '@/plugins/vueI18n'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(i18n)
app.use(VueQueryPlugin)

setLocale(i18n.global.locale.value)

app.mount('#app')
```

- [ ] **Step 3: 改 App.vue**

去掉 `ElConfigProvider`：

```vue
<template>
  <div :dir="rtl" class="dk-app">
    <router-view />
    <Toaster :theme="theme.mode" position="top-center" rich-colors />
    <ConfirmDialog />
  </div>
</template>
```

- [ ] **Step 4: 改 Vite plugins**

`build/vite/index.ts`：删除 `ElementPlusResolver` 与 `resolvers: [...]`（AutoImport / Components 都去掉 resolver）。保留 Components 的 globs（排除 ui）。

`build/vite/optimize.ts`：删除所有 `element-plus*` 与 `@element-plus/icons-vue` 预构建项。

- [ ] **Step 5: package.json / tsconfig**

```bash
npm uninstall element-plus @element-plus/icons-vue
```

`tsconfig.json`：从 `"types"` 数组去掉 `"element-plus/global"`。

若 `unplugin-vue-components` 仅因 Element 存在，可保留（仍服务非 ui 组件 dts）；不必强行卸载该插件。

- [ ] **Step 6: 清理 styles**

打开 `src/styles/index.scss`：把 `var(--el-*)` 换成 `var(--foreground)` / `var(--background)` 等，或硬改为与 globals 一致的语义。

- [ ] **Step 7: 全量验收**

```bash
rg "element-plus|@element-plus|<el-" src build package.json
npm run ts:check
npm run lint
npm run build
```

Expected：rg 无业务残留；build 通过。修复任何因卸载暴露的类型/导入错误。

手动回归清单：

- [ ] 官网首页无青绿；登录/注册 CTA 正常  
- [ ] 门户占位、Buy、订单仍正常  
- [ ] Admin：用户/节点/Host/设置 CRUD 与确认框  
- [ ] 语言切换、主题切换、侧栏折叠、TagsView  

- [ ] **Step 8: Commit**

```bash
git add -A
git commit -m "chore(dashboard): remove Element Plus after full shadcn migration"
```

---

## Spec Coverage Checklist

| Spec 项 | Task |
|---------|------|
| SiteLayout + Home | 2 |
| Placeholder | 3 |
| LanguageSwitch / ThemeToggle | 3 |
| Admin 壳 | 4 |
| Setting 页 | 5 |
| Node | 6 |
| Host | 7 |
| User 列表区 | 8 |
| User 对话框 | 9 |
| 卸载 Element | 10 |
| Dialog/Switch/Select 基建 | 1 |
| 非目标（新功能/占位业务） | 全局约束 |

## Self-Review Notes

- 确认流统一为已有 `useConfirm`，避免再造一套。
- User/Host 表单字段多：计划要求「字段一一替换」并保留 model 逻辑，禁止只改外壳留 `el-*`。
- Element 卸载是硬门禁：Task 10 Step 1 必须零残留再改依赖。
