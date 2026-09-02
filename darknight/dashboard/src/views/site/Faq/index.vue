<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'
import { usePageSeo } from '@/composables/usePageSeo'

const { t } = useI18n()
const router = useRouter()

usePageSeo({
  titleKey: 'site.faq.seoTitle',
  descriptionKey: 'site.faq.seoDescription',
  withHreflang: true,
  withFaqSchema: true,
  faqSchema: {
    count: 7,
    questionKey: (i) => `site.faq.q${i}`,
    answerKey: (i) => `site.faq.a${i}`
  }
})

const faqItems = [1, 2, 3, 4, 5, 6, 7] as const
</script>

<template>
  <section class="flex flex-col gap-8">
    <header class="text-center">
      <h1 class="m-0 text-3xl font-bold text-foreground">{{ t('site.faq.title') }}</h1>
      <p class="mx-auto mt-3 max-w-2xl text-sm leading-relaxed text-muted-foreground">
        {{ t('site.faq.subtitle') }}
      </p>
    </header>

    <div class="rounded-xl border border-border bg-card p-6 sm:p-8">
      <div class="flex flex-col gap-3">
        <details
          v-for="item in faqItems"
          :key="item"
          class="group rounded-lg border border-border px-4 py-3 open:bg-muted/30"
        >
          <summary
            class="cursor-pointer list-none text-sm font-medium text-foreground marker:content-none [&::-webkit-details-marker]:hidden"
          >
            <span class="flex items-start justify-between gap-3">
              <span>{{ t(`site.faq.q${item}`) }}</span>
              <span class="text-muted-foreground transition group-open:rotate-45">+</span>
            </span>
          </summary>
          <p class="mb-0 mt-3 text-sm leading-relaxed text-muted-foreground">
            {{ t(`site.faq.a${item}`) }}
          </p>
        </details>
      </div>
    </div>

    <div class="flex flex-col items-center gap-3 sm:flex-row sm:justify-center">
      <Button @click="router.push({ name: 'site-guides' })">
        {{ t('site.faq.viewGuides') }}
      </Button>
      <Button variant="outline" @click="router.push({ name: 'portal-register' })">
        {{ t('site.home.getStarted') }}
      </Button>
    </div>
  </section>
</template>
