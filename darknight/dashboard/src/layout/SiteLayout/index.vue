<script setup lang="ts">
import { watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import LanguageSwitch from '@/components/LanguageSwitch/index.vue'
import SiteLegalFooter from '@/components/SiteLegalFooter/index.vue'
import { Button } from '@/components/ui/button'

const { t, locale } = useI18n()
const route = useRoute()
const router = useRouter()

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
      <div class="mx-auto flex h-16 max-w-5xl items-center justify-between gap-6 px-6">
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
    <SiteLegalFooter />
  </div>
</template>
