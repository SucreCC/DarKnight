<script setup lang="ts">
import { computed } from 'vue'
import { useThemeStore } from '@/store/modules/theme'
import { useI18n } from 'vue-i18n'
import { Toaster } from '@/components/ui/sonner'
import ConfirmDialog from '@/components/ConfirmDialog/index.vue'

const theme = useThemeStore()
const { locale } = useI18n()
const rtl = computed(() => (locale.value === 'fa' ? 'rtl' : 'ltr'))
</script>

<template>
  <div :dir="rtl" class="dk-app">
    <router-view />
    <Toaster :theme="theme.mode" position="top-center" rich-colors />
    <ConfirmDialog />
  </div>
</template>

<style scoped>
.dk-app {
  width: 100%;
  height: 100%;
}
</style>
