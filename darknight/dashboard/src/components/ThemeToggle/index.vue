<script setup lang="ts">
import { computed } from 'vue'
import { Moon, Sun } from 'lucide-vue-next'
import { useThemeStore } from '@/store/modules/theme'
import { Button } from '@/components/ui/button'

const theme = useThemeStore()
const isDark = computed(() => theme.mode === 'dark')
</script>

<template>
  <Button variant="ghost" size="icon" type="button" @click="theme.toggle()">
    <Moon v-if="isDark" class="size-4" />
    <Sun v-else class="size-4" />
  </Button>
</template>
