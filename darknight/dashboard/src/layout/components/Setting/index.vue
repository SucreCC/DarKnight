<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAppStore } from '@/store/modules/app'
import { useThemeStore } from '@/store/modules/theme'

const visible = defineModel<boolean>({ required: true })

const { t } = useI18n()
const appStore = useAppStore()
const themeStore = useThemeStore()

const isDark = computed({
  get: () => themeStore.mode === 'dark',
  set: (value: boolean) => themeStore.setMode(value ? 'dark' : 'light')
})
</script>

<template>
  <el-drawer v-model="visible" :title="t('layout.settings')" size="300px">
    <div class="setting-item">
      <span>{{ t('layout.darkMode') }}</span>
      <el-switch v-model="isDark" />
    </div>
    <div class="setting-item">
      <span>{{ t('layout.breadcrumb') }}</span>
      <el-switch
        :model-value="appStore.showBreadcrumb"
        @update:model-value="appStore.setShowBreadcrumb($event as boolean)"
      />
    </div>
    <div class="setting-item">
      <span>{{ t('layout.tagsView') }}</span>
      <el-switch
        :model-value="appStore.showTagsView"
        @update:model-value="appStore.setShowTagsView($event as boolean)"
      />
    </div>
  </el-drawer>
</template>

<style scoped>
.setting-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0;
}
</style>
