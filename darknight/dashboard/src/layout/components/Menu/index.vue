<script setup lang="ts">
import { computed, type Component } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Link, Network, Settings, ShoppingBag, Users } from 'lucide-vue-next'
import { routes } from '@/router'
import { useAppStore } from '@/store/modules/app'
import { cn } from '@/lib/utils'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const appStore = useAppStore()

const menuItems = computed(() => {
  const root = routes.find((r) => r.path === '/admin')
  return (root?.children ?? []).filter((child) => child.meta?.title)
})

const activeMenu = computed(() => route.name as string)

const iconMap: Record<string, Component> = {
  Users,
  Network,
  Link,
  ShoppingBag,
  Settings
}

function onSelect(name: string) {
  router.push({ name })
}
</script>

<template>
  <div
    class="flex h-15 shrink-0 items-center gap-2.5 overflow-hidden whitespace-nowrap px-5"
    :class="appStore.collapsed ? 'justify-center px-2' : undefined"
  >
    <img src="/statics/logo.png" class="size-8 shrink-0 rounded-lg object-contain" alt="DarKnight" />
    <span v-show="!appStore.collapsed" class="text-xl font-bold text-foreground">DarKnight</span>
  </div>
  <nav class="flex flex-1 flex-col gap-1 overflow-auto p-2">
    <button
      v-for="item in menuItems"
      :key="item.name as string"
      type="button"
      :title="t(item.meta!.title as string)"
      :class="
        cn(
          'flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm transition-colors',
          appStore.collapsed && 'justify-center px-2',
          activeMenu === item.name
            ? 'bg-primary/10 font-medium text-primary'
            : 'text-foreground hover:bg-muted'
        )
      "
      @click="onSelect(item.name as string)"
    >
      <component
        :is="iconMap[item.meta!.icon as string] || Users"
        class="size-4 shrink-0"
      />
      <span v-show="!appStore.collapsed">{{ t(item.meta!.title as string) }}</span>
    </button>
  </nav>
</template>
