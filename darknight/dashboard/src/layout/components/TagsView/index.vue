<script setup lang="ts">
import { computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import type { TabPaneName } from 'element-plus'
import { useTagsViewStore } from '@/store/modules/tagsView'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const tagsViewStore = useTagsViewStore()

watch(
  () => route.name,
  () => {
    if (route.name) tagsViewStore.addView(route)
  },
  { immediate: true }
)

const activeName = computed(() => route.name as string)

/** 只剩一个标签时不允许关闭，否则会退化成空白页 */
const closable = computed(() => tagsViewStore.visitedViews.length > 1)

function onTabClick(name: TabPaneName) {
  if (name !== route.name) router.push({ name: name as string })
}

function onTabRemove(name: TabPaneName) {
  const next = tagsViewStore.removeView(name as string)
  if (name === route.name && next) {
    router.push({ name: next.name })
  }
}
</script>

<template>
  <el-tabs
    :model-value="activeName"
    type="card"
    class="tags-view"
    @tab-change="onTabClick"
    @tab-remove="onTabRemove"
  >
    <el-tab-pane
      v-for="view in tagsViewStore.visitedViews"
      :key="view.name"
      :name="view.name"
      :label="t(view.title)"
      :closable="closable"
    />
  </el-tabs>
</template>

<style scoped>
.tags-view {
  padding: 6px 16px 0;
  border-bottom: 1px solid var(--el-border-color);
  flex-shrink: 0;
  background: var(--el-bg-color);
}

.tags-view :deep(.el-tabs__header) {
  margin: 0;
}

.tags-view :deep(.el-tabs__content) {
  display: none;
}

.tags-view :deep(.el-tabs__nav) {
  border: none;
}

.tags-view :deep(.el-tabs__item) {
  height: 30px;
  margin-right: 6px;
  line-height: 30px;
  border: 1px solid var(--el-border-color);
  border-radius: 4px;
}

.tags-view :deep(.el-tabs__item.is-active) {
  color: #fff;
  background-color: var(--el-color-primary);
  border-color: var(--el-color-primary);
}
</style>
