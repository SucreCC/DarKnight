<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  percent: number
  label: string
}>()

const starburstPath = computed(() => {
  const cx = 50
  const cy = 50
  const spikes = 12
  const outer = 46
  const inner = 30
  const step = Math.PI / spikes
  let path = ''

  for (let i = 0; i < spikes * 2; i++) {
    const radius = i % 2 === 0 ? outer : inner
    const angle = i * step - Math.PI / 2
    const x = cx + Math.cos(angle) * radius
    const y = cy + Math.sin(angle) * radius
    path += `${i === 0 ? 'M' : 'L'}${x.toFixed(2)},${y.toFixed(2)} `
  }

  return `${path}Z`
})
</script>

<template>
  <div
    v-if="percent > 0"
    class="relative flex size-[4rem] rotate-12 items-center justify-center text-primary-foreground"
    aria-hidden="true"
  >
    <svg class="absolute inset-0 size-full drop-shadow-md" viewBox="0 0 100 100">
      <path class="fill-primary" :d="starburstPath" />
    </svg>

    <div class="relative z-10 -rotate-12 flex flex-col items-center justify-center px-1 text-center leading-none">
      <span class="text-[10px] font-semibold tracking-wide">{{ label }}</span>
      <span class="mt-0.5 text-base font-extrabold leading-none">{{ percent }}%</span>
    </div>
  </div>

  <span
    v-else
    class="inline-flex max-w-[4.5rem] rounded-full bg-muted px-2 py-1 text-center text-[10px] font-medium leading-tight text-muted-foreground"
  >
    {{ label }}
  </span>
</template>
