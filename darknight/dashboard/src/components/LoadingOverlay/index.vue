<script setup lang="ts">
import { Loader2 } from 'lucide-vue-next'

defineProps<{ loading?: boolean }>()
</script>

<template>
  <div class="relative">
    <slot />
    <div
      v-if="loading"
      class="absolute inset-0 z-10 flex items-center justify-center rounded-[inherit] bg-background/70 backdrop-blur-[1px]"
    >
      <Loader2 class="size-6 animate-spin text-primary" />
    </div>
  </div>
</template>
