<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type { AdminTicketListItem } from '@/api/ticket'
import { formatTicketTime, type TicketPriority, type TicketStatus } from '@/api/portal/tickets'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'

defineProps<{ tickets: AdminTicketListItem[]; loading: boolean }>()
const emit = defineEmits<{ open: [ticket: AdminTicketListItem] }>()

const { t } = useI18n()

const PRIORITY_VARIANT: Record<
  TicketPriority,
  'secondary' | 'outline' | 'default' | 'destructive'
> = {
  low: 'secondary',
  normal: 'outline',
  high: 'default',
  urgent: 'destructive'
}

const STATUS_VARIANT: Record<
  TicketStatus,
  'secondary' | 'default' | 'outline' | 'destructive'
> = {
  open: 'default',
  pending: 'secondary',
  resolved: 'outline',
  closed: 'secondary'
}
</script>

<template>
  <div class="overflow-x-auto rounded-xl border border-border bg-card">
    <div v-if="loading && !tickets.length" class="space-y-3 p-4">
      <Skeleton v-for="i in 5" :key="i" class="h-10 w-full" />
    </div>

    <div
      v-else-if="!tickets.length"
      class="flex flex-col items-center gap-3 px-4 py-10 text-center text-muted-foreground"
    >
      <p class="text-sm">{{ t('admin.tickets.empty') }}</p>
    </div>

    <table v-else class="w-full min-w-[960px] text-sm">
      <thead class="border-b border-border text-muted-foreground">
        <tr>
          <th class="px-4 py-3 text-start font-medium">#</th>
          <th class="px-4 py-3 text-start font-medium">{{ t('admin.tickets.username') }}</th>
          <th class="px-4 py-3 text-start font-medium">{{ t('portal.tickets.subject') }}</th>
          <th class="px-4 py-3 text-start font-medium">{{ t('portal.tickets.priority') }}</th>
          <th class="px-4 py-3 text-start font-medium">{{ t('portal.tickets.statusLabel') }}</th>
          <th class="px-4 py-3 text-start font-medium">{{ t('portal.tickets.createdAt') }}</th>
          <th class="px-4 py-3 text-start font-medium">{{ t('portal.tickets.lastReply') }}</th>
          <th class="px-4 py-3 text-end font-medium" />
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="row in tickets"
          :key="row.id"
          class="border-b border-border last:border-0"
        >
          <td class="px-4 py-3 text-foreground">{{ row.id }}</td>
          <td class="px-4 py-3 text-foreground">{{ row.username }}</td>
          <td class="max-w-[220px] truncate px-4 py-3" :title="row.subject">
            {{ row.subject }}
          </td>
          <td class="px-4 py-3">
            <Badge :variant="PRIORITY_VARIANT[row.priority]">
              {{ t(`portal.tickets.priority.${row.priority}`) }}
            </Badge>
          </td>
          <td class="px-4 py-3">
            <Badge :variant="STATUS_VARIANT[row.status]">
              {{ t(`portal.tickets.status.${row.status}`) }}
            </Badge>
          </td>
          <td class="px-4 py-3 text-muted-foreground">
            {{ formatTicketTime(row.created_at) }}
          </td>
          <td class="px-4 py-3 text-muted-foreground">
            {{ formatTicketTime(row.last_reply_at) }}
          </td>
          <td class="px-4 py-3 text-end">
            <Button size="sm" variant="outline" type="button" @click="emit('open', row)">
              {{ t('admin.tickets.handle') }}
            </Button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
