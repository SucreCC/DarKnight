<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { useQuery, useQueryClient } from '@tanstack/vue-query'
import { Plus } from 'lucide-vue-next'
import {
  fetchPortalTickets,
  formatTicketTime,
  type TicketListItem,
  type TicketPriority,
  type TicketStatus
} from '@/api/portal/tickets'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import CreateTicketDialog from './components/CreateTicketDialog.vue'
import TicketDetailDialog from './components/TicketDetailDialog.vue'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const queryClient = useQueryClient()

const createOpen = ref(false)
const detailOpen = ref(false)
const activeTicket = ref<TicketListItem | null>(null)

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

const { data, isLoading, isError } = useQuery({
  queryKey: ['portal', 'tickets'],
  queryFn: fetchPortalTickets,
  refetchOnWindowFocus: false
})

function openDetail(row: TicketListItem) {
  activeTicket.value = row
  detailOpen.value = true
}

function onCreated() {
  queryClient.invalidateQueries({ queryKey: ['portal', 'tickets'] })
}

function openFromRoute() {
  const raw = route.params.ticketId ?? route.query.ticketId
  const id = Number(raw)
  if (!Number.isFinite(id) || id <= 0) return
  const row = (data.value ?? []).find((item) => item.id === id)
  if (row) {
    openDetail(row)
    return
  }
  activeTicket.value = {
    id,
    subject: '',
    priority: 'normal',
    status: 'open',
    created_at: '',
    last_reply_at: null
  }
  detailOpen.value = true
}

onMounted(() => {
  if (route.params.ticketId || route.query.ticketId) {
    openFromRoute()
  }
})

watch(
  () => data.value,
  () => {
    if (route.params.ticketId || route.query.ticketId) {
      openFromRoute()
    }
  }
)

watch(detailOpen, (open) => {
  if (!open && (route.name === 'portal-ticket-detail' || route.query.ticketId)) {
    router.replace({ name: 'portal-tickets' })
  }
})
</script>

<template>
  <div class="max-w-6xl">
    <div class="mb-4 flex items-center justify-between gap-3">
      <h1 class="text-lg font-semibold text-foreground">{{ t('portal.tickets.title') }}</h1>
      <Button type="button" @click="createOpen = true">
        <Plus class="mr-2 size-4" />
        {{ t('portal.tickets.create') }}
      </Button>
    </div>

    <Alert v-if="isError" variant="destructive" class="mb-4">
      <AlertDescription>{{ t('portal.requestFailed') }}</AlertDescription>
    </Alert>

    <div class="overflow-x-auto rounded-xl border border-border bg-card">
      <div v-if="isLoading" class="space-y-3 p-4">
        <Skeleton v-for="i in 5" :key="i" class="h-10 w-full" />
      </div>

      <div
        v-else-if="!(data ?? []).length"
        class="flex flex-col items-center gap-3 py-10 text-muted-foreground"
      >
        <p>{{ t('portal.tickets.empty') }}</p>
        <Button type="button" @click="createOpen = true">
          {{ t('portal.tickets.create') }}
        </Button>
      </div>

      <table v-else class="w-full min-w-[800px] text-sm">
        <thead class="border-b border-border text-muted-foreground">
          <tr>
            <th class="px-4 py-3 text-start font-medium">#</th>
            <th class="px-4 py-3 text-start font-medium">{{ t('portal.tickets.subject') }}</th>
            <th class="px-4 py-3 text-start font-medium">{{ t('portal.tickets.priority') }}</th>
            <th class="px-4 py-3 text-start font-medium">{{ t('portal.tickets.statusLabel') }}</th>
            <th class="px-4 py-3 text-start font-medium">{{ t('portal.tickets.createdAt') }}</th>
            <th class="px-4 py-3 text-start font-medium">{{ t('portal.tickets.lastReply') }}</th>
            <th class="px-4 py-3 text-end font-medium">{{ t('portal.orders.action') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="row in data"
            :key="row.id"
            class="border-b border-border last:border-0"
          >
            <td class="px-4 py-3">
              <button
                type="button"
                class="text-primary hover:underline"
                @click="openDetail(row)"
              >
                {{ row.id }}
              </button>
            </td>
            <td class="max-w-[240px] truncate px-4 py-3" :title="row.subject">
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
              <Button size="sm" variant="outline" @click="openDetail(row)">
                {{ t('portal.orders.detail') }}
              </Button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <CreateTicketDialog v-model="createOpen" @created="onCreated" />
    <TicketDetailDialog v-model="detailOpen" :ticket-row="activeTicket" />
  </div>
</template>
