<script setup lang="ts">
import { computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { X } from 'lucide-vue-next'
import { useTagsViewStore } from '@/store/modules/tagsView'
import { cn } from '@/lib/utils'

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
const closable = computed(() => tagsViewStore.visitedViews.length > 1)

function onTabClick(name: string) {
  if (name !== route.name) router.push({ name })
}

function onTabRemove(name: string) {
  const next = tagsViewStore.removeView(name)
  if (name === route.name && next) {
    router.push({ name: next.name })
  }
}
</script>

<template>
  <div class="flex gap-2 overflow-x-auto border-b border-border bg-card px-3 py-2">
    <button
      v-for="view in tagsViewStore.visitedViews"
      :key="view.name"
      type="button"
      :class="
        cn(
          'inline-flex items-center gap-1 rounded-md border px-2.5 py-1 text-xs transition-colors',
          activeName === view.name
            ? 'border-primary/30 bg-primary/10 text-primary'
            : 'border-border text-muted-foreground hover:bg-muted'
        )
      "
      @click="onTabClick(view.name)"
    >
      <span>{{ t(view.title) }}</span>
      <span
        v-if="closable"
        role="button"
        tabindex="0"
        class="inline-flex rounded-sm p-0.5 hover:bg-muted"
        @click.stop="onTabRemove(view.name)"
        @keydown.enter.stop="onTabRemove(view.name)"
      >
        <X class="size-3" />
      </span>
    </button>
  </div>
</template>
