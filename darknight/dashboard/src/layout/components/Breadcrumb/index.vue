<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const route = useRoute()

const items = computed(() =>
  route.matched.filter((item) => item.meta?.title).map((item) => t(item.meta.title as string))
)
</script>

<template>
  <nav class="flex items-center gap-2 text-sm text-muted-foreground">
    <template v-for="(item, index) in items" :key="item">
      <span v-if="index > 0">/</span>
      <span :class="index === items.length - 1 ? 'font-medium text-foreground' : undefined">
        {{ item }}
      </span>
    </template>
  </nav>
</template>
