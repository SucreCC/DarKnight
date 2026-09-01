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
