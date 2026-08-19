import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { RouteLocationNormalized } from 'vue-router'

export interface VisitedView {
  /** 路由 name，同时用作 el-tabs 的 tab 标识 */
  name: string
  /** i18n key，渲染时才翻译，切换语言后标签文字会跟着变 */
  title: string
  path: string
}

export const useTagsViewStore = defineStore('tagsView', () => {
  const visitedViews = ref<VisitedView[]>([])

  function addView(route: RouteLocationNormalized) {
    const name = route.name as string
    if (!name || visitedViews.value.some((v) => v.name === name)) return
    visitedViews.value.push({
      name,
      title: (route.meta.title as string) || name,
      path: route.path
    })
  }

  /** 删除标签，并返回删除后应当激活的标签（已无标签时返回 undefined） */
  function removeView(name: string): VisitedView | undefined {
    const index = visitedViews.value.findIndex((v) => v.name === name)
    if (index === -1) return undefined
    visitedViews.value.splice(index, 1)
    return visitedViews.value[index] ?? visitedViews.value[index - 1]
  }

  function removeOthers(name: string) {
    visitedViews.value = visitedViews.value.filter((v) => v.name === name)
  }

  function reset() {
    visitedViews.value = []
  }

  return { visitedViews, addView, removeView, removeOthers, reset }
})
