<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useDebounceFn } from '@vueuse/core'
import { Plus, Search } from 'lucide-vue-next'
import type { UserFilters } from '@/api/user/types'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from '@/components/ui/select'

const props = defineProps<{
  search: string
  status?: UserFilters['status']
}>()

const emit = defineEmits<{
  'update:search': [value: string]
  'update:status': [value: UserFilters['status']]
  create: []
  resetAll: []
}>()

const { t } = useI18n()

/** Reka Select disallows empty-string item values. */
const ALL_STATUS = '__all__'

const searchInput = ref(props.search)
const emitSearch = useDebounceFn((v: string) => emit('update:search', v), 300)
function onSearch(v: string | number) {
  const text = String(v)
  searchInput.value = text
  emitSearch(text)
}

const statusOptions: {
  label: string
  value: NonNullable<UserFilters['status']>
}[] = [
  { label: 'status.active', value: 'active' },
  { label: 'status.on_hold', value: 'on_hold' },
  { label: 'status.disabled', value: 'disabled' },
  { label: 'status.limited', value: 'limited' },
  { label: 'status.expired', value: 'expired' }
]

function statusSelectValue() {
  return props.status ?? ALL_STATUS
}

function onStatusChange(value: string | number | bigint | Record<string, unknown> | null) {
  const v = String(value ?? ALL_STATUS)
  emit('update:status', (v === ALL_STATUS ? undefined : v) as UserFilters['status'])
}
</script>

<template>
  <div class="flex flex-wrap items-center gap-3">
    <div class="relative w-full max-w-[260px]">
      <Search class="pointer-events-none absolute start-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
      <Input
        :model-value="searchInput"
        :placeholder="t('search')"
        class="ps-9"
        @update:model-value="onSearch"
      />
    </div>

    <Select :model-value="statusSelectValue()" @update:model-value="onStatusChange">
      <SelectTrigger class="w-[160px]">
        <SelectValue :placeholder="t('usersTable.status')" />
      </SelectTrigger>
      <SelectContent>
        <SelectItem :value="ALL_STATUS">{{ t('usersTable.status') }}</SelectItem>
        <SelectItem v-for="opt in statusOptions" :key="opt.value" :value="opt.value">
          {{ t(opt.label) }}
        </SelectItem>
      </SelectContent>
    </Select>

    <div class="flex-1" />

    <Button variant="outline" type="button" @click="emit('resetAll')">
      {{ t('resetAllUsage') }}
    </Button>
    <Button type="button" @click="emit('create')">
      <Plus class="size-4" />
      {{ t('createUser') }}
    </Button>
  </div>
</template>
