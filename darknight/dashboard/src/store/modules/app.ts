import { defineStore } from 'pinia'
import { ref } from 'vue'

const COLLAPSE_KEY = 'darknight-sidebar-collapse'
const BREADCRUMB_KEY = 'darknight-show-breadcrumb'
const TAGS_VIEW_KEY = 'darknight-show-tags-view'

/** 未设置过时取默认值，避免首次访问就被当成关闭 */
function readFlag(key: string, fallback: boolean): boolean {
  const saved = localStorage.getItem(key)
  return saved === null ? fallback : saved === '1'
}

function writeFlag(key: string, value: boolean): void {
  localStorage.setItem(key, value ? '1' : '0')
}

export const useAppStore = defineStore('app', () => {
  const collapsed = ref(readFlag(COLLAPSE_KEY, false))
  const showBreadcrumb = ref(readFlag(BREADCRUMB_KEY, true))
  const showTagsView = ref(readFlag(TAGS_VIEW_KEY, true))

  function setCollapsed(value: boolean) {
    collapsed.value = value
    writeFlag(COLLAPSE_KEY, value)
  }

  function toggleCollapsed() {
    setCollapsed(!collapsed.value)
  }

  function setShowBreadcrumb(value: boolean) {
    showBreadcrumb.value = value
    writeFlag(BREADCRUMB_KEY, value)
  }

  function setShowTagsView(value: boolean) {
    showTagsView.value = value
    writeFlag(TAGS_VIEW_KEY, value)
  }

  return {
    collapsed,
    showBreadcrumb,
    showTagsView,
    setCollapsed,
    toggleCollapsed,
    setShowBreadcrumb,
    setShowTagsView
  }
})
