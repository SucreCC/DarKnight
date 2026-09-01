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
    <footer
      class="border-t border-border bg-card px-6 py-5 text-center text-[13px] text-muted-foreground"
    >
      {{ t('site.footer') }}
    </footer>
  </div>
</template>
