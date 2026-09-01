<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { ChevronDown } from 'lucide-vue-next'
import { SUPPORTED_LOCALES, setLocale, type LocaleCode } from '@/plugins/vueI18n'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger
} from '@/components/ui/dropdown-menu'

const { locale } = useI18n()

const currentLabel = computed(
  () => SUPPORTED_LOCALES.find((item) => item.value === locale.value)?.label ?? locale.value
)

function onChange(value: LocaleCode) {
  setLocale(value)
}
</script>

<template>
  <DropdownMenu>
    <DropdownMenuTrigger as-child>
      <Button variant="outline" class="min-w-[7.5rem] justify-between gap-2">
        <span>{{ currentLabel }}</span>
        <ChevronDown class="size-4 opacity-60" />
      </Button>
    </DropdownMenuTrigger>
    <DropdownMenuContent align="end" class="min-w-[7.5rem]">
      <DropdownMenuItem
        v-for="item in SUPPORTED_LOCALES"
        :key="item.value"
        @click="onChange(item.value)"
      >
        {{ item.label }}
      </DropdownMenuItem>
    </DropdownMenuContent>
  </DropdownMenu>
</template>
