# 仪表盘流量使用卡 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在门户仪表盘公告下方增加全宽流量使用卡（进度条 + 百分比 + 剩余），并去掉订阅卡内重复的文字流量行。

**Architecture:** 仅改 `Dashboard/index.vue` 与四语言 i18n。用量计算内联或同文件 `computed`；复用 `formatBytes` 与 `Badge`。有 `subscription_url` 才渲染流量卡；`data_limit` 为 `null` 或 `0` 视为不限。

**Tech Stack:** Vue 3、Tailwind、shadcn Badge、vue-i18n、现有 `fetchPortalMe`

**Spec:** `docs/superpowers/specs/2026-09-01-dashboard-traffic-card-design.md`

## Global Constraints

- 命令在 `e:\kai\DarKnight\darknight\dashboard` 执行。
- 不改后端、不新增 API。
- 无订阅不渲染流量卡；有订阅时去掉订阅卡内文字流量行。
- 阈值：`<80%` primary；`≥80%` amber；`≥100%` destructive。
- i18n 扁平键，四文件同步：`zh.json` `en.json` `ru.json` `fa.json`。
- 验收：`npm run build`；提交信息 `feat(dashboard): ...`。

## File Map

| 文件 | 职责 |
|------|------|
| `src/views/portal/Dashboard/index.vue` | 流量卡 UI + 计算 + 布局 |
| `src/locales/{zh,en,ru,fa}.json` | 新文案键 |

---

### Task 1: i18n 键

**Files:**
- Modify: `src/locales/zh.json`、`en.json`、`ru.json`、`fa.json`

**Interfaces:**
- Produces 键：
  - `portal.dashboard.trafficUsage`
  - `portal.dashboard.trafficRemaining`（含 `{ remaining }`）
  - `portal.dashboard.trafficUnlimited`
  - `portal.dashboard.trafficUsedOf`（含 `{ used }` `{ total }`，底行左侧）

- [ ] **Step 1: 写入四语言**

`zh.json`：

```json
"portal.dashboard.trafficUsage": "流量使用",
"portal.dashboard.trafficRemaining": "剩余 {remaining}",
"portal.dashboard.trafficUnlimited": "不限",
"portal.dashboard.trafficUsedOf": "{used} / {total}"
```

`en.json`：

```json
"portal.dashboard.trafficUsage": "Traffic usage",
"portal.dashboard.trafficRemaining": "{remaining} left",
"portal.dashboard.trafficUnlimited": "Unlimited",
"portal.dashboard.trafficUsedOf": "{used} / {total}"
```

`ru.json`（语义对等）：

```json
"portal.dashboard.trafficUsage": "Использование трафика",
"portal.dashboard.trafficRemaining": "Осталось {remaining}",
"portal.dashboard.trafficUnlimited": "Безлимит",
"portal.dashboard.trafficUsedOf": "{used} / {total}"
```

`fa.json`（语义对等）：

```json
"portal.dashboard.trafficUsage": "مصرف ترافیک",
"portal.dashboard.trafficRemaining": "{remaining} باقی‌مانده",
"portal.dashboard.trafficUnlimited": "نامحدود",
"portal.dashboard.trafficUsedOf": "{used} / {total}"
```

插在现有 `portal.dashboard.traffic` 附近，保持 JSON 合法逗号。

- [ ] **Step 2: Commit**

```bash
git add src/locales/zh.json src/locales/en.json src/locales/ru.json src/locales/fa.json
git commit -m "feat(dashboard): add i18n for traffic usage card"
```

---

### Task 2: Dashboard 流量卡

**Files:**
- Modify: `src/views/portal/Dashboard/index.vue`

**Interfaces:**
- Consumes: `PortalUser`、`formatBytes`、`Badge`、Task 1 文案键
- Produces: 公告下全宽流量卡；订阅卡无文字流量行

- [ ] **Step 1: 在 script 增加计算**

在现有 `user` ref 旁加入（`import { computed }`）：

```ts
function isUnlimited(limit: number | null | undefined): boolean {
  return limit === null || limit === undefined || limit === 0
}

const hasSubscription = computed(() => !!user.value?.subscription_url)

const trafficPercent = computed(() => {
  const u = user.value
  if (!u || isUnlimited(u.data_limit)) return 0
  return Math.min(100, Math.round((u.used_traffic / (u.data_limit as number)) * 100))
})

const trafficRemaining = computed(() => {
  const u = user.value
  if (!u || isUnlimited(u.data_limit)) return 0
  return Math.max(0, (u.data_limit as number) - u.used_traffic)
})

const trafficBarClass = computed(() => {
  const p = trafficPercent.value
  if (p >= 100) return 'bg-destructive'
  if (p >= 80) return 'bg-amber-500'
  return 'bg-primary'
})

const trafficPercentClass = computed(() => {
  const p = trafficPercent.value
  if (p >= 100) return 'text-destructive'
  if (p >= 80) return 'text-amber-600 dark:text-amber-400'
  return 'text-muted-foreground'
})
```

- [ ] **Step 2: 模板 — 公告后插入流量卡；订阅卡去掉流量行**

公告卡后、`md:grid-cols-2` 网格前：

```vue
    <div
      v-if="hasSubscription && user"
      class="rounded-xl border border-border bg-card p-5"
    >
      <div class="mb-3 flex items-center justify-between gap-3">
        <h2 class="text-base font-semibold text-foreground">
          {{ t('portal.dashboard.trafficUsage') }}
        </h2>
        <template v-if="isUnlimited(user.data_limit)">
          <Badge variant="secondary">{{ t('portal.dashboard.trafficUnlimited') }}</Badge>
        </template>
        <span v-else :class="['text-sm font-medium', trafficPercentClass]">
          {{ trafficPercent }}%
        </span>
      </div>

      <template v-if="!isUnlimited(user.data_limit)">
        <div class="mb-3 h-2.5 overflow-hidden rounded-full bg-muted">
          <div
            class="h-full rounded-full transition-[width] duration-300"
            :class="trafficBarClass"
            :style="{ width: `${trafficPercent}%` }"
          />
        </div>
        <div class="flex items-center justify-between gap-3 text-sm text-muted-foreground">
          <span>
            {{
              t('portal.dashboard.trafficUsedOf', {
                used: formatBytes(user.used_traffic),
                total: formatBytes(user.data_limit as number)
              })
            }}
          </span>
          <span>
            {{
              t('portal.dashboard.trafficRemaining', {
                remaining: formatBytes(trafficRemaining)
              })
            }}
          </span>
        </div>
      </template>

      <p v-else class="text-sm text-muted-foreground">
        {{ formatBytes(user.used_traffic) }}
      </p>
    </div>
```

订阅卡内删除：

```vue
          <p class="text-sm text-foreground">
            <span class="font-medium">{{ t('portal.dashboard.traffic') }}:</span>
            {{ formatBytes(user.used_traffic) }}
            <template v-if="user.data_limit"> / {{ formatBytes(user.data_limit) }}</template>
          </p>
```

保留 status 与复制链接。

- [ ] **Step 3: 验收**

```bash
npm run build
```

手动：有限额看进度条与阈值色；`data_limit` 0/null 见不限；无订阅无卡；订阅卡无重复流量行。

- [ ] **Step 4: Commit**

```bash
git add src/views/portal/Dashboard/index.vue
git commit -m "feat(dashboard): show traffic usage card on portal dashboard"
```

---

## Spec Coverage

| Spec | Task |
|------|------|
| 全宽卡在公告下 | 2 |
| 进度条/百分比/剩余 | 2 |
| 阈值色 | 2 |
| 不限 / 无订阅 | 2 |
| 订阅卡去重 | 2 |
| i18n | 1 |
| 不改 API | 全局约束 |
