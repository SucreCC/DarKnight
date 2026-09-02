<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type { TicketFilters } from '@/api/ticket'
import type { TicketPriority, TicketStatus } from '@/api/portal/tickets'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from '@/components/ui/select'

const props = defineProps<{ modelValue: TicketFilters }>()
const emit = defineEmits<{ 'update:modelValue': [value: TicketFilters] }>()

const { t } = useI18n()

const STATUSES: TicketStatus[] = ['open', 'pending', 'resolved', 'closed']
const PRIORITIES: TicketPriority[] = ['low', 'normal', 'high', 'urgent']

function patch(partial: Partial<TicketFilters>) {
  emit('update:modelValue', { ...props.modelValue, ...partial })
}
</script>

<template>
  <div class="mb-4 flex flex-wrap items-end gap-4">
    <div class="space-y-2">
      <Label>{{ t('admin.tickets.filterStatus') }}</Label>
      <Select
        :model-value="modelValue.status || 'all'"
        @update:model-value="(v) => patch({ status: v === 'all' ? '' : (v as TicketStatus) })"
      >
        <SelectTrigger class="w-[160px]">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">{{ t('admin.tickets.filterAll') }}</SelectItem>
          <SelectItem v-for="s in STATUSES" :key="s" :value="s">
            {{ t(`portal.tickets.status.${s}`) }}
          </SelectItem>
        </SelectContent>
      </Select>
    </div>

    <div class="space-y-2">
      <Label>{{ t('admin.tickets.filterPriority') }}</Label>
      <Select
        :model-value="modelValue.priority || 'all'"
        @update:model-value="(v) => patch({ priority: v === 'all' ? '' : (v as TicketPriority) })"
      >
        <SelectTrigger class="w-[160px]">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">{{ t('admin.tickets.filterAll') }}</SelectItem>
          <SelectItem v-for="p in PRIORITIES" :key="p" :value="p">
            {{ t(`portal.tickets.priority.${p}`) }}
          </SelectItem>
        </SelectContent>
      </Select>
    </div>
  </div>
</template>
