<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useDebounceFn } from '@vueuse/core'
import { Plus, Search } from '@element-plus/icons-vue'
import type { UserFilters } from '@/api/user/types'

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

const searchInput = ref(props.search)
const emitSearch = useDebounceFn((v: string) => emit('update:search', v), 300)
function onSearch(v: string) {
  searchInput.value = v
  emitSearch(v)
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
</script>

<template>
  <div class="dk-toolbar">
    <el-input
      :model-value="searchInput"
      :placeholder="t('search')"
      :prefix-icon="Search"
      clearable
      style="width: 260px"
      @update:model-value="onSearch"
    />
    <el-select
      :model-value="status ?? ''"
      :placeholder="t('usersTable.status')"
      clearable
      style="width: 160px"
      @update:model-value="
        (v: string) => emit('update:status', (v || undefined) as UserFilters['status'])
      "
    >
      <el-option
        v-for="opt in statusOptions"
        :key="opt.value"
        :label="t(opt.label)"
        :value="opt.value"
      />
    </el-select>

    <div class="dk-spacer" />

    <el-button @click="emit('resetAll')">{{ t('resetAllUsage') }}</el-button>
    <el-button type="primary" :icon="Plus" @click="emit('create')">
      {{ t('createUser') }}
    </el-button>
  </div>
</template>
