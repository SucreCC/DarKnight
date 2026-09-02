<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Check, ChevronDown, Globe } from 'lucide-vue-next'
import { SUPPORTED_LOCALES, setLocale, type LocaleCode } from '@/plugins/vueI18n'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuRadioGroup,
  DropdownMenuRadioItem,
  DropdownMenuTrigger
} from '@/components/ui/dropdown-menu'

const { locale } = useI18n()

const currentLabel = computed(
  () => SUPPORTED_LOCALES.find((item) => item.value === locale.value)?.label ?? locale.value
)

function onChange(value: string) {
  setLocale(value as LocaleCode)
}
</script>

<template>
  <DropdownMenu>
    <DropdownMenuTrigger as-child>
      <Button
        variant="ghost"
        size="sm"
        class="h-9 gap-1.5 px-2.5 font-normal text-foreground hover:bg-accent/60"
      >
        <Globe class="size-4 text-muted-foreground" />
        <span class="max-w-24 truncate">{{ currentLabel }}</span>
        <ChevronDown class="size-3.5 text-muted-foreground/70" />
      </Button>
    </DropdownMenuTrigger>
    <DropdownMenuContent align="end" class="min-w-36">
      <DropdownMenuRadioGroup :model-value="locale" @update:model-value="onChange">
        <DropdownMenuRadioItem
          v-for="item in SUPPORTED_LOCALES"
          :key="item.value"
          :value="item.value"
          class="pl-8"
        >
          <template #indicator-icon>
            <Check class="size-3.5" />
          </template>
          {{ item.label }}
        </DropdownMenuRadioItem>
      </DropdownMenuRadioGroup>
    </DropdownMenuContent>
  </DropdownMenu>
</template>
