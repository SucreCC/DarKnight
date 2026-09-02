<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Cable, FileText, Lock } from 'lucide-vue-next'
import type { Component } from 'vue'
import { Button } from '@/components/ui/button'
import { useSiteSeo } from '@/composables/useSiteSeo'

const { t } = useI18n()
const router = useRouter()

useSiteSeo()

const features: { icon: Component; title: string; desc: string }[] = [
  { icon: Lock, title: 'site.home.feature1Title', desc: 'site.home.feature1Desc' },
  { icon: Cable, title: 'site.home.feature2Title', desc: 'site.home.feature2Desc' },
  { icon: FileText, title: 'site.home.feature3Title', desc: 'site.home.feature3Desc' }
]

const protocols = ['VLESS', 'VMess', 'Trojan', 'Shadowsocks'] as const

const faqItems = [1, 2, 3, 4, 5] as const

const quickLinks = [
  { name: 'site-pricing' as const, titleKey: 'site.menu.pricing', descKey: 'site.home.quickPricing' },
  { name: 'site-guides' as const, titleKey: 'site.menu.guides', descKey: 'site.home.quickGuides' },
  { name: 'site-faq' as const, titleKey: 'site.menu.faq', descKey: 'site.home.quickFaq' }
]
</script>

<template>
  <section class="flex flex-col gap-8">
    <div
      class="rounded-2xl bg-primary px-6 py-12 text-center text-primary-foreground sm:px-10 sm:py-14"
    >
      <h1 class="m-0 text-3xl font-bold sm:text-4xl">{{ t('site.home.heroTitle') }}</h1>
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
          @click="router.push({ name: 'site-pricing' })"
        >
          {{ t('site.menu.pricing') }}
        </Button>
      </div>
    </div>

    <div class="grid gap-4 sm:grid-cols-3">
      <button
        v-for="link in quickLinks"
        :key="link.name"
        type="button"
        class="rounded-xl border border-border bg-card p-5 text-left transition hover:border-primary/40 hover:bg-primary/5"
        @click="router.push({ name: link.name })"
      >
        <p class="m-0 text-base font-semibold text-foreground">{{ t(link.titleKey) }}</p>
        <p class="mb-0 mt-2 text-sm leading-relaxed text-muted-foreground">{{ t(link.descKey) }}</p>
      </button>
    </div>

    <div class="grid gap-5 md:grid-cols-3">
      <article
        v-for="item in features"
        :key="item.title"
        class="min-h-44 rounded-xl border border-border bg-card p-6"
      >
        <component :is="item.icon" class="mb-3 size-7 text-primary" aria-hidden="true" />
        <h2 class="mb-2 text-lg font-semibold text-foreground">{{ t(item.title) }}</h2>
        <p class="m-0 text-sm leading-relaxed text-muted-foreground">{{ t(item.desc) }}</p>
      </article>
    </div>

    <section class="rounded-xl border border-border bg-card p-6 sm:p-8">
      <h2 class="m-0 text-xl font-semibold text-foreground">{{ t('site.home.protocolsTitle') }}</h2>
      <p class="mt-3 mb-5 text-sm leading-relaxed text-muted-foreground">
        {{ t('site.home.protocolsDesc') }}
      </p>
      <ul class="m-0 flex list-none flex-wrap gap-2 p-0">
        <li
          v-for="protocol in protocols"
          :key="protocol"
          class="rounded-full border border-primary/20 bg-primary/5 px-3 py-1 text-sm font-medium text-primary"
        >
          {{ protocol }}
        </li>
      </ul>
    </section>

    <section class="rounded-xl border border-border bg-card p-6 sm:p-8">
      <h2 class="m-0 text-xl font-semibold text-foreground">{{ t('site.home.aboutTitle') }}</h2>
      <p class="mt-3 m-0 text-sm leading-relaxed text-muted-foreground">
        {{ t('site.home.aboutDesc') }}
      </p>
    </section>

    <section class="rounded-xl border border-border bg-card p-6 sm:p-8">
      <div class="flex flex-wrap items-end justify-between gap-3">
        <h2 class="m-0 text-xl font-semibold text-foreground">{{ t('site.home.faqTitle') }}</h2>
        <Button variant="link" class="h-auto p-0" @click="router.push({ name: 'site-faq' })">
          {{ t('site.home.viewAllFaq') }}
        </Button>
      </div>
      <div class="mt-5 flex flex-col gap-3">
        <details
          v-for="item in faqItems"
          :key="item"
          class="group rounded-lg border border-border px-4 py-3 open:bg-muted/30"
        >
          <summary
            class="cursor-pointer list-none text-sm font-medium text-foreground marker:content-none [&::-webkit-details-marker]:hidden"
          >
            <span class="flex items-start justify-between gap-3">
              <span>{{ t(`site.home.faq${item}Q`) }}</span>
              <span class="text-muted-foreground transition group-open:rotate-45">+</span>
            </span>
          </summary>
          <p class="mb-0 mt-3 text-sm leading-relaxed text-muted-foreground">
            {{ t(`site.home.faq${item}A`) }}
          </p>
        </details>
      </div>
    </section>
  </section>
</template>
