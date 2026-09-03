<script setup lang="ts">
import { computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import LanguageSwitch from '@/components/LanguageSwitch/index.vue'
import SiteLegalFooter from '@/components/SiteLegalFooter/index.vue'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

const { t, locale } = useI18n()
const route = useRoute()
const router = useRouter()

const navItems = [
  { name: 'site-home' as const, labelKey: 'site.menu.home' },
  { name: 'site-pricing' as const, labelKey: 'site.menu.pricing' },
  { name: 'site-guides' as const, labelKey: 'site.menu.guides' },
  { name: 'site-faq' as const, labelKey: 'site.menu.faq' },
  { name: 'site-blog' as const, labelKey: 'site.menu.blog' }
]

const activeRoute = computed(() => route.name)

function isNavActive(name: (typeof navItems)[number]['name']): boolean {
  if (activeRoute.value === name) return true
  return name === 'site-blog' && activeRoute.value === 'site-blog-detail'
}

watch(locale, (value) => {
  if (route.meta.zone !== 'site') return
  const query = { ...route.query }
  if (value === 'en') {
    delete query.lang
  } else {
    query.lang = value
  }
  router.replace({ query })
})
</script>

<template>
  <div class="flex min-h-screen flex-col bg-muted/40">
    <header class="border-b border-border bg-card">
      <div class="mx-auto flex max-w-5xl flex-col gap-3 px-6 py-3 sm:h-16 sm:flex-row sm:items-center sm:justify-between sm:gap-6 sm:py-0">
        <div class="flex items-center justify-between gap-4">
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
          <div class="flex items-center gap-2 sm:hidden">
            <LanguageSwitch />
            <Button size="sm" variant="outline" @click="router.push({ name: 'login' })">
              {{ t('portal.login') }}
            </Button>
          </div>
        </div>

        <nav class="flex flex-wrap items-center gap-1 text-sm" aria-label="Primary">
          <button
            v-for="item in navItems"
            :key="item.name"
            type="button"
            :class="
              cn(
                'rounded-md px-2.5 py-1.5 transition-colors',
                isNavActive(item.name)
                  ? 'bg-primary/10 font-medium text-primary'
                  : 'text-muted-foreground hover:bg-muted hover:text-foreground'
              )
            "
            @click="router.push({ name: item.name })"
          >
            {{ t(item.labelKey) }}
          </button>
        </nav>

        <div class="hidden items-center gap-3 sm:flex">
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
    <SiteLegalFooter />
  </div>
</template>
