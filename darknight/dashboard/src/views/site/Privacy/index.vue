<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { usePageSeo } from '@/composables/usePageSeo'
import { SITE_CONTACT_EMAIL } from '@/config/site'

const { t } = useI18n()

usePageSeo({
  titleKey: 'site.legal.privacySeoTitle',
  descriptionKey: 'site.legal.privacySeoDescription'
})

const sections = [1, 2, 3, 4, 5, 6] as const
</script>

<template>
  <article class="rounded-xl border border-border bg-card p-6 sm:p-8">
    <h1 class="m-0 text-2xl font-bold text-foreground">{{ t('site.legal.privacyTitle') }}</h1>
    <p class="mt-3 text-sm leading-relaxed text-muted-foreground">
      {{ t('site.legal.lastUpdated') }}
    </p>
    <p class="mt-4 text-sm leading-relaxed text-muted-foreground">
      {{ t('site.legal.privacyIntro') }}
    </p>

    <section v-for="section in sections" :key="section" class="mt-6">
      <h2 class="m-0 text-lg font-semibold text-foreground">
        {{ t(`site.legal.privacyS${section}Title`) }}
      </h2>
      <p class="mt-2 m-0 text-sm leading-relaxed text-muted-foreground">
        {{ t(`site.legal.privacyS${section}Body`) }}
      </p>
    </section>

    <p class="mt-6 text-sm leading-relaxed text-muted-foreground">
      {{ t('site.legal.contactLead') }}
      <a :href="`mailto:${SITE_CONTACT_EMAIL}`" class="text-primary hover:underline">
        {{ SITE_CONTACT_EMAIL }}
      </a>
    </p>
  </article>
</template>
