<script setup lang="ts">
import { computed, ref } from 'vue'
import { useAppStore } from '@/store/modules/app'
import Menu from './components/Menu/index.vue'
import ToolHeader from './components/ToolHeader/index.vue'
import TagsView from './components/TagsView/index.vue'
import Setting from './components/Setting/index.vue'

const appStore = useAppStore()
const settingVisible = ref(false)
const asideWidth = computed(() => (appStore.collapsed ? '64px' : '220px'))
</script>

<template>
  <div class="flex h-screen w-full overflow-hidden">
    <aside
      class="flex shrink-0 flex-col overflow-hidden border-e border-border bg-card transition-[width,flex-basis] duration-200"
      :style="{ width: asideWidth, flexBasis: asideWidth }"
    >
      <Menu />
    </aside>
    <div class="flex min-w-0 flex-1 flex-col overflow-hidden">
      <ToolHeader @open-setting="settingVisible = true" />
      <TagsView v-if="appStore.showTagsView" />
      <main class="flex-1 overflow-auto bg-muted/40 p-4">
        <router-view />
      </main>
    </div>
  </div>
  <Setting v-model="settingVisible" />
</template>
