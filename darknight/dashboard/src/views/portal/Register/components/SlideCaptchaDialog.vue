<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

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

const visible = computed({
  get: () => props.modelValue,
  set: (v: boolean) => emit('update:modelValue', v)
})

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
      visible.value = false
    }, 280)
  } else {
    failed.value = true
    offsetX.value = 0
  }
}

function onClosed() {
  reset()
}

onBeforeUnmount(() => {
  dragging.value = false
})
</script>

<template>
  <el-dialog
    v-model="visible"
    :title="t('portal.slideCaptchaTitle')"
    width="360px"
    align-center
    :close-on-click-modal="false"
    @closed="onClosed"
  >
    <p class="hint">{{ t('portal.slideCaptchaHint') }}</p>
    <div
      ref="trackRef"
      class="track"
      :class="{ ok: verified, bad: failed }"
    >
      <div class="progress" :style="{ width: `${progressWidth}px` }" />
      <span class="track-text">
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
        class="handle"
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
  </el-dialog>
</template>

<style scoped>
.hint {
  margin: 0 0 16px;
  color: #606266;
  font-size: 14px;
}

.track {
  position: relative;
  height: 44px;
  overflow: hidden;
  user-select: none;
  background: #f2f3f5;
  border-radius: 6px;
  touch-action: none;
}

.track.ok {
  background: #e8f8f5;
}

.track.bad {
  animation: shake 0.28s ease;
}

.progress {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  background: rgb(32 163 151 / 22%);
  pointer-events: none;
}

.track.ok .progress {
  background: rgb(32 163 151 / 35%);
}

.track-text {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #909399;
  font-size: 13px;
  pointer-events: none;
}

.track.ok .track-text {
  color: #20a397;
}

.handle {
  position: absolute;
  top: 0;
  left: 0;
  z-index: 1;
  width: 44px;
  height: 44px;
  margin: 0;
  padding: 0;
  color: #20a397;
  font-size: 18px;
  font-weight: 700;
  cursor: grab;
  background: #fff;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  box-shadow: 0 1px 4px rgb(0 0 0 / 8%);
}

.handle:active {
  cursor: grabbing;
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
