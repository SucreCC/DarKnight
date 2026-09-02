<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { SITE_CONTACT_EMAIL } from '@/config/site'

const { t } = useI18n()
</script>

<template>
  <footer class="mt-6 space-y-2 text-center text-xs text-muted-foreground">
    <p class="m-0 font-medium text-foreground/80">{{ t('site.auth.trustNotice') }}</p>
    <p class="m-0">{{ t('site.auth.officialDomain') }}</p>
    <nav class="flex flex-wrap items-center justify-center gap-x-3 gap-y-1">
      <router-link :to="{ name: 'site-privacy' }" class="hover:text-foreground">
        {{ t('site.legal.privacy') }}
      </router-link>
      <span aria-hidden="true">·</span>
      <router-link :to="{ name: 'site-terms' }" class="hover:text-foreground">
        {{ t('site.legal.terms') }}
      </router-link>
      <span aria-hidden="true">·</span>
      <a :href="`mailto:${SITE_CONTACT_EMAIL}`" class="hover:text-foreground">
        {{ SITE_CONTACT_EMAIL }}
      </a>
    </nav>
  </footer>
</template>
