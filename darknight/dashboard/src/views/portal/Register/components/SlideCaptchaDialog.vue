<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  AlertDialog,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogHeader,
  AlertDialogTitle
} from '@/components/ui/alert-dialog'
import { cn } from '@/lib/utils'

const props = defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  success: []
}>()

const { t } = useI18n()

const trackRef = ref<HTMLElement | null>(null)
const dragging = ref(false)
const offsetX = ref(0)
const verified = ref(false)
const failed = ref(false)
const trackWidth = ref(280)

const handleSize = 44
const passThreshold = 8

const maxOffset = computed(() => Math.max(0, trackWidth.value - handleSize))
const progressWidth = computed(() => offsetX.value + handleSize / 2)

function measure() {
  if (trackRef.value) {
    trackWidth.value = trackRef.value.clientWidth
  }
}

function reset() {
  dragging.value = false
  offsetX.value = 0
  verified.value = false
  failed.value = false
}

watch(
  () => props.modelValue,
  async (open) => {
    if (open) {
      reset()
      await nextTick()
      measure()
    } else {
      reset()
    }
  }
)

function onPointerDown(e: PointerEvent) {
  if (verified.value) return
  dragging.value = true
  failed.value = false
  ;(e.currentTarget as HTMLElement).setPointerCapture(e.pointerId)
}

function onPointerMove(e: PointerEvent) {
  if (!dragging.value || !trackRef.value) return
  const rect = trackRef.value.getBoundingClientRect()
  const x = e.clientX - rect.left - handleSize / 2
  offsetX.value = Math.min(maxOffset.value, Math.max(0, x))
}

function onPointerUp() {
  if (!dragging.value) return
  dragging.value = false
  if (offsetX.value >= maxOffset.value - passThreshold) {
    offsetX.value = maxOffset.value
    verified.value = true
    window.setTimeout(() => {
      emit('success')
      emit('update:modelValue', false)
    }, 280)
  } else {
    failed.value = true
    offsetX.value = 0
  }
}

onBeforeUnmount(() => {
  dragging.value = false
})
</script>

<template>
  <AlertDialog
    :open="props.modelValue"
    @update:open="(v: boolean) => emit('update:modelValue', v)"
  >
    <AlertDialogContent class="sm:max-w-sm">
      <AlertDialogHeader>
        <AlertDialogTitle>{{ t('portal.slideCaptchaTitle') }}</AlertDialogTitle>
        <AlertDialogDescription>{{ t('portal.slideCaptchaHint') }}</AlertDialogDescription>
      </AlertDialogHeader>

      <div
        ref="trackRef"
        :class="
          cn(
            'relative h-11 touch-none overflow-hidden rounded-md bg-muted select-none',
            verified && 'bg-primary/10',
            failed && 'track-bad'
          )
        "
      >
        <div
          class="pointer-events-none absolute inset-y-0 start-0 bg-primary/20"
          :class="verified ? 'bg-primary/35' : undefined"
          :style="{ width: `${progressWidth}px` }"
        />
        <span
          :class="
            cn(
              'pointer-events-none absolute inset-0 flex items-center justify-center text-[13px] text-muted-foreground',
              verified && 'text-primary'
            )
          "
        >
          {{
            verified
              ? t('portal.slideCaptchaOk')
              : failed
                ? t('portal.slideCaptchaRetry')
                : t('portal.slideCaptchaDrag')
          }}
        </span>
        <button
          type="button"
          class="absolute start-0 top-0 z-[1] flex size-11 cursor-grab items-center justify-center rounded-md border border-border bg-card text-lg font-bold text-primary shadow-sm active:cursor-grabbing"
          :style="{ transform: `translateX(${offsetX}px)` }"
          :aria-label="t('portal.slideCaptchaDrag')"
          @pointerdown="onPointerDown"
          @pointermove="onPointerMove"
          @pointerup="onPointerUp"
          @pointercancel="onPointerUp"
        >
          ››
        </button>
      </div>
    </AlertDialogContent>
  </AlertDialog>
</template>

<style scoped>
.track-bad {
  animation: shake 0.28s ease;
}

@keyframes shake {
  0%,
  100% {
    transform: translateX(0);
  }

  25% {
    transform: translateX(-4px);
  }

  75% {
    transform: translateX(4px);
  }
}
</style>
