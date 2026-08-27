<script setup lang="ts">
import { computed } from 'vue'
import { ElConfigProvider } from 'element-plus'
import { useThemeStore } from '@/store/modules/theme'
import { useI18n } from 'vue-i18n'
import { Toaster } from '@/components/ui/sonner'
import ConfirmDialog from '@/components/ConfirmDialog/index.vue'

// Ensure theme store is initialized (applies dark class on load).
const theme = useThemeStore()
const { locale } = useI18n()
const rtl = computed(() => (locale.value === 'fa' ? 'rtl' : 'ltr'))
</script>

<template>
  <el-config-provider :locale="undefined">
    <div :dir="rtl" class="dk-app">
      <router-view />
      <Toaster :theme="theme.mode" position="top-center" rich-colors />
      <ConfirmDialog />
    </div>
  </el-config-provider>
</template>

<style scoped>
.dk-app {
  width: 100%;
  height: 100%;
}
</style>
