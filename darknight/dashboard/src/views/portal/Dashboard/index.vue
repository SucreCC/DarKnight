<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { BookOpen, LifeBuoy, Link2, Package, Plus, ShoppingCart } from 'lucide-vue-next'
import type { Component } from 'vue'
import { fetchPortalMe } from '@/api/portal'
import type { PortalUser } from '@/api/portal/types'
import { pickLocale } from '../Buy/plans'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

const { t, locale } = useI18n()
const router = useRouter()
const user = ref<PortalUser | null>(null)

const shortcuts: {
  title: string
  desc: string
  icon: Component
  route?: string
  action?: string
}[] = [
  {
    title: 'portal.dashboard.shortcutDocs',
    desc: 'portal.dashboard.shortcutDocsDesc',
    icon: BookOpen,
    route: 'portal-docs'
  },
  {
    title: 'portal.dashboard.shortcutSubscribe',
    desc: 'portal.dashboard.shortcutSubscribeDesc',
    icon: Link2,
    action: 'copySub'
  },
  {
    title: 'portal.dashboard.shortcutBuy',
    desc: 'portal.dashboard.shortcutBuyDesc',
    icon: ShoppingCart,
    route: 'portal-buy'
  },
  {
    title: 'portal.dashboard.shortcutSupport',
    desc: 'portal.dashboard.shortcutSupportDesc',
    icon: LifeBuoy,
    route: 'portal-tickets'
  }
]

const hasSubscription = computed(() => !!user.value?.subscription_url)

const currentPlanName = computed(() => {
  const u = user.value
  if (!u) return ''
  const name = pickLocale(locale.value, u.plan_name_zh ?? '', u.plan_name_en ?? '')
  return name || u.plan_id || ''
})

const expireLabel = computed(() => {
  const expire = user.value?.expire
  if (!expire) return ''
  const date = new Date(expire * 1000)
  const pad = (n: number) => String(n).padStart(2, '0')
  const formatted = `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`
  return t('portal.dashboard.planExpires', { date: formatted })
})

onMounted(async () => {
  user.value = await fetchPortalMe()
})

async function copySubscription() {
  if (!user.value?.subscription_url) return
  await navigator.clipboard.writeText(user.value.subscription_url)
}

function onShortcut(item: (typeof shortcuts)[number]) {
  if (item.action === 'copySub') {
    copySubscription()
    return
  }
  if (item.route) router.push({ name: item.route })
}
</script>

<template>
  <div class="flex max-w-6xl flex-col gap-5">
    <div class="rounded-2xl border border-slate-200/80 bg-card p-6 shadow-sm dark:border-border">
      <Badge>{{ t('portal.dashboard.announcement') }}</Badge>
      <p class="mt-3 text-sm text-foreground">{{ t('portal.dashboard.announcementText') }}</p>
      <p class="mt-2 text-xs text-muted-foreground">2026-08-19</p>
    </div>

    <div
      v-if="hasSubscription && user"
      class="rounded-2xl border border-slate-200/80 bg-card p-6 shadow-sm dark:border-border"
    >
      <div class="mb-4 flex items-center justify-between gap-3">
        <h2 class="flex items-center gap-2 text-base font-semibold text-foreground">
          <Package class="size-4 text-primary" />
          {{ t('portal.dashboard.trafficUsage') }}
        </h2>
        <Badge v-if="user.status === 'active'" variant="secondary">
          {{ t('portal.dashboard.statusActive') }}
        </Badge>
      </div>

      <p class="text-2xl font-semibold tracking-tight text-foreground">
        {{ currentPlanName || t('portal.dashboard.noPlan') }}
      </p>
      <p v-if="expireLabel" class="mt-2 text-sm text-muted-foreground">
        {{ expireLabel }}
      </p>
    </div>

    <div class="grid gap-5 md:grid-cols-2">
      <div class="rounded-2xl border border-slate-200/80 bg-card p-6 shadow-sm dark:border-border">
        <h2 class="mb-4 text-base font-semibold text-foreground">
          {{ t('portal.dashboard.mySubscription') }}
        </h2>
        <div v-if="user?.subscription_url" class="space-y-3">
          <p class="text-sm text-foreground">
            <span class="font-medium">{{ t('portal.dashboard.status') }}:</span>
            {{ user.status }}
          </p>
          <div class="flex gap-2">
            <Input :model-value="user.subscription_url" readonly class="flex-1" />
            <Button type="button" @click="copySubscription">
              {{ t('portal.dashboard.copy') }}
            </Button>
          </div>
        </div>
        <button
          v-else
          type="button"
          class="flex min-h-44 w-full flex-col items-center justify-center gap-2 rounded-xl border border-dashed border-slate-200 text-muted-foreground transition-colors hover:bg-slate-50 dark:border-border dark:hover:bg-muted/50"
          @click="router.push({ name: 'portal-buy' })"
        >
          <Plus class="size-10 text-primary" />
          <span>{{ t('portal.dashboard.buySubscription') }}</span>
        </button>
      </div>

      <div class="rounded-2xl border border-slate-200/80 bg-card p-6 shadow-sm dark:border-border">
        <h2 class="mb-2 text-base font-semibold text-foreground">
          {{ t('portal.dashboard.shortcuts') }}
        </h2>
        <button
          v-for="item in shortcuts"
          :key="item.title"
          type="button"
          class="flex w-full items-center justify-between gap-3 rounded-xl px-2 py-3.5 text-start transition-colors hover:bg-slate-50 last:border-b-0 dark:hover:bg-muted/50"
          @click="onShortcut(item)"
        >
          <div>
            <div class="font-semibold text-foreground">{{ t(item.title) }}</div>
            <div class="mt-1 text-[13px] text-muted-foreground">{{ t(item.desc) }}</div>
          </div>
          <component :is="item.icon" class="size-5 shrink-0 text-primary/70" />
        </button>
      </div>
    </div>
  </div>
</template>
