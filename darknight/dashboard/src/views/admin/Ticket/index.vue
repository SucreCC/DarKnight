<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { AdminTicketListItem, TicketFilters as TicketFilterState } from '@/api/ticket'
import { useTicketsQuery } from '@/api/ticket'
import TicketDetailDialog from './components/TicketDetailDialog.vue'
import TicketFiltersBar from './components/TicketFilters.vue'
import TicketsTable from './components/TicketsTable.vue'

const { t } = useI18n()

const filters = ref<TicketFilterState>({ status: '', priority: '', offset: 0, limit: 50 })
const { data, isFetching } = useTicketsQuery(() => ({ ...filters.value }))

const tickets = computed<AdminTicketListItem[]>(() => data.value ?? [])
const dialogOpen = ref(false)
const activeTicket = ref<AdminTicketListItem | null>(null)

function onOpen(ticket: AdminTicketListItem) {
  activeTicket.value = ticket
  dialogOpen.value = true
}
</script>

<template>
  <div>
    <h1 class="mb-4 text-lg font-semibold text-foreground">{{ t('admin.tickets.title') }}</h1>

    <TicketFiltersBar v-model="filters" />
    <TicketsTable :tickets="tickets" :loading="isFetching" @open="onOpen" />
    <TicketDetailDialog v-model="dialogOpen" :ticket-row="activeTicket" />
  </div>
</template>
