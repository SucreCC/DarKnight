<script setup lang="ts">
import type { HTMLAttributes } from 'vue'
import { computed, ref, useAttrs } from 'vue'
import { useI18n } from 'vue-i18n'
import { Eye, EyeOff } from 'lucide-vue-next'
import { useVModel } from '@vueuse/core'
import { cn } from '@/lib/utils'

defineOptions({ inheritAttrs: false })

const props = defineProps<{
  modelValue?: string
  class?: HTMLAttributes['class']
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()

const { t } = useI18n()
const attrs = useAttrs()
const modelValue = useVModel(props, 'modelValue', emit, { passive: true })
const visible = ref(false)
const inputType = computed(() => (visible.value ? 'text' : 'password'))
const toggleLabel = computed(() =>
  visible.value ? t('portal.hidePassword') : t('portal.showPassword')
)

function toggleVisible() {
  visible.value = !visible.value
}
</script>

<template>
  <div class="relative">
    <input
      v-model="modelValue"
      v-bind="attrs"
      :type="inputType"
      data-slot="input"
      :class="
        cn(
          'file:text-foreground placeholder:text-muted-foreground selection:bg-primary selection:text-primary-foreground dark:bg-input/30 border-input h-9 w-full min-w-0 rounded-md border bg-transparent px-3 py-1 pe-10 text-base shadow-xs transition-[color,box-shadow] outline-none file:inline-flex file:h-7 file:border-0 file:bg-transparent file:text-sm file:font-medium disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50 md:text-sm',
          'focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-3',
          'aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive',
          props.class
        )
      "
    />
    <button
      type="button"
      tabindex="-1"
      class="absolute inset-y-0 end-0 flex items-center px-3 text-muted-foreground transition-colors hover:text-foreground"
      :aria-label="toggleLabel"
      @click="toggleVisible"
    >
      <EyeOff v-if="visible" class="size-4" />
      <Eye v-else class="size-4" />
    </button>
  </div>
</template>
