<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { BookOpen, LifeBuoy, Link2, Plus, ShoppingCart } from 'lucide-vue-next'
import type { Component } from 'vue'
import { fetchPortalMe } from '@/api/portal'
import type { PortalUser } from '@/api/portal/types'
import { formatBytes } from '@/utils/formatter'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

const { t } = useI18n()
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
  <div class="flex max-w-6xl flex-col gap-4">
    <div class="rounded-xl border border-border bg-card p-5">
      <Badge variant="secondary">{{ t('portal.dashboard.announcement') }}</Badge>
      <p class="mt-3 text-sm text-foreground">{{ t('portal.dashboard.announcementText') }}</p>
      <p class="mt-2 text-xs text-muted-foreground">2026-08-19</p>
    </div>

    <div class="grid gap-4 md:grid-cols-2">
      <div class="rounded-xl border border-border bg-card p-5">
        <h2 class="mb-4 text-base font-semibold text-foreground">
          {{ t('portal.dashboard.mySubscription') }}
        </h2>
        <div v-if="user?.subscription_url" class="space-y-3">
          <p class="text-sm text-foreground">
            <span class="font-medium">{{ t('portal.dashboard.status') }}:</span>
            {{ user.status }}
          </p>
          <p class="text-sm text-foreground">
            <span class="font-medium">{{ t('portal.dashboard.traffic') }}:</span>
            {{ formatBytes(user.used_traffic) }}
            <template v-if="user.data_limit"> / {{ formatBytes(user.data_limit) }}</template>
          </p>
          <div class="flex gap-2">
            <Input :model-value="user.subscription_url" readonly class="flex-1" />
            <Button type="button" variant="outline" @click="copySubscription">
              {{ t('portal.dashboard.copy') }}
            </Button>
          </div>
        </div>
        <button
          v-else
          type="button"
          class="flex min-h-44 w-full flex-col items-center justify-center gap-2 rounded-lg border border-dashed border-border text-muted-foreground transition-colors hover:bg-muted/50"
          @click="router.push({ name: 'portal-buy' })"
        >
          <Plus class="size-10" />
          <span>{{ t('portal.dashboard.buySubscription') }}</span>
        </button>
      </div>

      <div class="rounded-xl border border-border bg-card p-5">
        <h2 class="mb-2 text-base font-semibold text-foreground">
          {{ t('portal.dashboard.shortcuts') }}
        </h2>
        <button
          v-for="item in shortcuts"
          :key="item.title"
          type="button"
          class="flex w-full items-center justify-between gap-3 border-b border-border py-3.5 text-start last:border-b-0"
          @click="onShortcut(item)"
        >
          <div>
            <div class="font-semibold text-foreground">{{ t(item.title) }}</div>
            <div class="mt-1 text-[13px] text-muted-foreground">{{ t(item.desc) }}</div>
          </div>
          <component :is="item.icon" class="size-5 shrink-0 text-muted-foreground" />
        </button>
      </div>
    </div>
  </div>
</template>
