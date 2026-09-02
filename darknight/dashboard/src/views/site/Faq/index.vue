<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'
import { SITE_CONTACT_EMAIL } from '@/config/site'
import { SITE_URL } from '@/config/seo'

const { t, locale } = useI18n()
const router = useRouter()

const faqItems = [1, 2, 3, 4, 5, 6, 7] as const
const previousTitle = typeof document !== 'undefined' ? document.title : ''

function answer(item: number): string {
  if (item === 7) {
    return t('site.faqPage.a7', { email: SITE_CONTACT_EMAIL })
  }
  return t(`site.faqPage.a${item}`)
}

onMounted(() => {
  document.title = t('site.faqPage.seoTitle')
  const desc = document.querySelector('meta[name="description"]')
  if (desc) desc.setAttribute('content', t('site.faqPage.seoDescription'))

  let canonical = document.querySelector('link[rel="canonical"]') as HTMLLinkElement | null
  if (!canonical) {
    canonical = document.createElement('link')
    canonical.rel = 'canonical'
    document.head.appendChild(canonical)
  }
  const langQuery = locale.value === 'en' ? '' : `?lang=${locale.value}`
  canonical.href = `${SITE_URL}/faq${langQuery}`
})

onUnmounted(() => {
  document.title = previousTitle
})
</script>

<template>
  <section class="flex flex-col gap-8">
    <header class="text-center">
      <h1 class="m-0 text-3xl font-bold text-foreground">{{ t('site.faqPage.title') }}</h1>
      <p class="mx-auto mt-3 max-w-2xl text-sm leading-relaxed text-muted-foreground">
        {{ t('site.faqPage.subtitle') }}
      </p>
    </header>

    <div class="rounded-xl border border-border bg-card p-6 sm:p-8">
      <div class="flex flex-col gap-3">
        <div
          v-for="item in faqItems"
          :key="item"
          class="rounded-lg border border-border px-4 py-3"
        >
          <p class="m-0 text-sm font-medium text-foreground">
            {{ t(`site.faqPage.q${item}`) }}
          </p>
          <p class="mb-0 mt-2 text-sm leading-relaxed text-muted-foreground">
            {{ answer(item) }}
          </p>
        </div>
      </div>
    </div>

    <div class="flex flex-col items-center gap-3 sm:flex-row sm:justify-center">
      <Button @click="router.push({ name: 'site-guides' })">
        {{ t('site.faqPage.viewGuides') }}
      </Button>
      <Button variant="outline" @click="router.push({ name: 'portal-register' })">
        {{ t('site.home.getStarted') }}
      </Button>
    </div>
  </section>
</template>
