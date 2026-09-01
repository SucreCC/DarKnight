<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'

const { t } = useI18n()
const route = useRoute()
</script>

<template>
  <div
    class="flex min-h-80 flex-col items-center justify-center gap-2 rounded-xl border border-border bg-card p-8 text-center"
  >
    <p class="font-medium text-foreground">{{ t(route.meta.title as string) }}</p>
    <p class="text-sm text-muted-foreground">{{ t('portal.comingSoon') }}</p>
  </div>
</template>
