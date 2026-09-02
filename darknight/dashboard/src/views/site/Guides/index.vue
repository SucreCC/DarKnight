<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Monitor, Smartphone, Tablet } from 'lucide-vue-next'
import type { Component } from 'vue'
import { Button } from '@/components/ui/button'
import { usePageSeo } from '@/composables/usePageSeo'
import { CLIENT_DOWNLOADS } from '@/views/portal/Docs/articles'

const { t } = useI18n()
const router = useRouter()

usePageSeo({
  titleKey: 'site.guides.seoTitle',
  descriptionKey: 'site.guides.seoDescription',
  withHreflang: true
})

const guides: {
  id: string
  icon: Component
  titleKey: string
  descKey: string
  downloads: { labelKey: string; url: string }[]
}[] = [
  {
    id: 'windows',
    icon: Monitor,
    titleKey: 'site.guides.windowsTitle',
    descKey: 'site.guides.windowsDesc',
    downloads: [
      { labelKey: 'portal.docs.windows.downloadX64', url: CLIENT_DOWNLOADS.clashVergeWinX64 },
      { labelKey: 'portal.docs.windows.downloadArm64', url: CLIENT_DOWNLOADS.clashVergeWinArm64 }
    ]
  },
  {
    id: 'macos',
    icon: Monitor,
    titleKey: 'site.guides.macosTitle',
    descKey: 'site.guides.macosDesc',
    downloads: [
      { labelKey: 'portal.docs.macos.downloadArm', url: CLIENT_DOWNLOADS.clashVergeMacArm },
      { labelKey: 'portal.docs.macos.downloadIntel', url: CLIENT_DOWNLOADS.clashVergeMacIntel }
    ]
  },
  {
    id: 'ios',
    icon: Smartphone,
    titleKey: 'site.guides.iosTitle',
    descKey: 'site.guides.iosDesc',
    downloads: [{ labelKey: 'portal.docs.ios.downloadBtn', url: CLIENT_DOWNLOADS.shadowrocket }]
  },
  {
    id: 'android',
    icon: Tablet,
    titleKey: 'site.guides.androidTitle',
    descKey: 'site.guides.androidDesc',
    downloads: [
      { labelKey: 'portal.docs.android.downloadBtn', url: CLIENT_DOWNLOADS.clashMetaAndroid }
    ]
  }
]
</script>

<template>
  <section class="flex flex-col gap-8">
    <header class="text-center">
      <h1 class="m-0 text-3xl font-bold text-foreground">{{ t('site.guides.title') }}</h1>
      <p class="mx-auto mt-3 max-w-2xl text-sm leading-relaxed text-muted-foreground">
        {{ t('site.guides.subtitle') }}
      </p>
    </header>

    <div class="grid gap-5 md:grid-cols-2">
      <article
        v-for="guide in guides"
        :key="guide.id"
        class="flex flex-col rounded-xl border border-border bg-card p-6"
      >
        <component :is="guide.icon" class="mb-3 size-7 text-primary" aria-hidden="true" />
        <h2 class="m-0 text-lg font-semibold text-foreground">{{ t(guide.titleKey) }}</h2>
        <p class="mt-2 mb-4 flex-1 text-sm leading-relaxed text-muted-foreground">
          {{ t(guide.descKey) }}
        </p>
        <div class="flex flex-col gap-2">
          <a
            v-for="item in guide.downloads"
            :key="item.url"
            :href="item.url"
            target="_blank"
            rel="noopener noreferrer"
            class="text-sm font-medium text-primary hover:underline"
          >
            {{ t(item.labelKey) }}
          </a>
        </div>
      </article>
    </div>

    <div class="rounded-xl border border-border bg-card p-6 text-center sm:p-8">
      <h2 class="m-0 text-lg font-semibold text-foreground">{{ t('site.guides.ctaTitle') }}</h2>
      <p class="mx-auto mt-2 max-w-xl text-sm leading-relaxed text-muted-foreground">
        {{ t('site.guides.ctaDesc') }}
      </p>
      <div class="mt-5 flex flex-col items-center justify-center gap-3 sm:flex-row">
        <Button class="h-10" @click="router.push({ name: 'portal-register' })">
          {{ t('site.home.getStarted') }}
        </Button>
        <Button variant="outline" class="h-10" @click="router.push({ name: 'login' })">
          {{ t('site.home.login') }}
        </Button>
      </div>
    </div>
  </section>
</template>
