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
  <div class="flex min-h-screen flex-col bg-slate-100 dark:bg-background">
    <header
      class="grid h-14 shrink-0 items-center border-b border-slate-200/80 bg-card px-6 shadow-sm grid-cols-[1fr_auto_1fr] dark:border-border"
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
      <aside
        class="w-[232px] shrink-0 overflow-auto border-e border-slate-200/80 bg-card dark:border-border"
      >
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
                  'flex w-full items-center gap-2 rounded-xl px-3 py-2.5 text-sm transition-colors',
                  activeMenu === item.name
                    ? 'bg-primary/10 font-medium text-primary'
                    : 'text-foreground hover:bg-slate-100 dark:hover:bg-muted'
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

      <main class="flex-1 overflow-auto p-6 md:p-8">
        <router-view />
      </main>
    </div>
  </div>
</template>
