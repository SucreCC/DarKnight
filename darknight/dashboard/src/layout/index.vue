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
  <div class="layout">
    <aside class="layout-aside" :style="{ width: asideWidth, flexBasis: asideWidth }">
      <Menu />
    </aside>
    <div class="layout-main">
      <ToolHeader @open-setting="settingVisible = true" />
      <TagsView v-if="appStore.showTagsView" />
      <main class="layout-content">
        <router-view />
      </main>
    </div>
  </div>
  <Setting v-model="settingVisible" />
</template>

<style scoped>
.layout {
  display: flex;
  width: 100%;
  height: 100vh;
  overflow: hidden;
}

.layout-aside {
  display: flex;
  overflow: hidden;
  border-right: 1px solid var(--el-border-color);
  transition: width var(--el-transition-duration), flex-basis var(--el-transition-duration);
  flex: 0 0 auto;
  flex-direction: column;
  background: var(--el-bg-color);
}

.layout-main {
  display: flex;
  overflow: hidden;
  flex: 1 1 0;
  flex-direction: column;
  min-width: 0;
}

.layout-content {
  padding: 16px;
  overflow: auto;
  flex: 1 1 auto;
  background: var(--el-bg-color-page);
}
</style>
