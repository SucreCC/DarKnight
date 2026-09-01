<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAppStore } from '@/store/modules/app'
import { useThemeStore } from '@/store/modules/theme'
import { Switch } from '@/components/ui/switch'

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
  <div v-if="visible" class="fixed inset-0 z-50">
    <button
      type="button"
      class="absolute inset-0 bg-black/50"
      aria-label="close"
      @click="visible = false"
    />
    <aside
      class="absolute inset-y-0 end-0 flex w-[300px] flex-col border-s border-border bg-card p-5 shadow-lg"
    >
      <h2 class="mb-2 text-base font-semibold text-foreground">{{ t('layout.settings') }}</h2>
      <div class="flex items-center justify-between py-3">
        <span class="text-sm text-foreground">{{ t('layout.darkMode') }}</span>
        <Switch
          :model-value="isDark"
          @update:model-value="(v: boolean) => (isDark = v)"
        />
      </div>
      <div class="flex items-center justify-between py-3">
        <span class="text-sm text-foreground">{{ t('layout.breadcrumb') }}</span>
        <Switch
          :model-value="appStore.showBreadcrumb"
          @update:model-value="(v: boolean) => appStore.setShowBreadcrumb(v)"
        />
      </div>
      <div class="flex items-center justify-between py-3">
        <span class="text-sm text-foreground">{{ t('layout.tagsView') }}</span>
        <Switch
          :model-value="appStore.showTagsView"
          @update:model-value="(v: boolean) => appStore.setShowTagsView(v)"
        />
      </div>
    </aside>
  </div>
</template>
