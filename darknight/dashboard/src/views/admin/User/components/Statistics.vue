<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useQuery } from '@tanstack/vue-query'
import { Activity, Cpu, Users } from 'lucide-vue-next'
import { http } from '@/config/axios'
import { formatBytes, numberWithCommas } from '@/utils/formatter'

type SystemStats = {
  version: string
  users_active: number
  total_user: number
  incoming_bandwidth: number
  outgoing_bandwidth: number
  mem_used: number
  mem_total: number
}

const { t } = useI18n()
const { data } = useQuery({
  queryKey: ['system'],
  queryFn: () => http<SystemStats>('/system'),
  refetchInterval: 5000
})

const memPercent = computed(() => {
  if (!data.value || !data.value.mem_total) return 0
  return Math.min((data.value.mem_used / data.value.mem_total) * 100, 100)
})
</script>

<template>
  <div class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
    <div class="rounded-xl border border-border bg-card p-4">
      <div class="flex items-start gap-3">
        <Users class="mt-0.5 size-5 text-primary" />
        <div class="min-w-0 flex-1">
          <p class="text-sm text-muted-foreground">{{ t('activeUsers') }}</p>
          <p class="text-2xl font-bold text-foreground">
            {{ data ? numberWithCommas(data.users_active) : '-' }}
            <span class="text-sm font-normal text-muted-foreground">
              / {{ data ? numberWithCommas(data.total_user) : '-' }}
            </span>
          </p>
        </div>
      </div>
    </div>

    <div class="rounded-xl border border-border bg-card p-4">
      <div class="flex items-start gap-3">
        <Activity class="mt-0.5 size-5 text-primary" />
        <div class="min-w-0 flex-1">
          <p class="text-sm text-muted-foreground">{{ t('dataUsage') }}</p>
          <p class="text-2xl font-bold text-foreground">
            {{ data ? formatBytes(data.incoming_bandwidth + data.outgoing_bandwidth) : '-' }}
          </p>
        </div>
      </div>
    </div>

    <div class="rounded-xl border border-border bg-card p-4">
      <div class="flex items-start gap-3">
        <Cpu class="mt-0.5 size-5 text-primary" />
        <div class="min-w-0 flex-1">
          <p class="text-sm text-muted-foreground">{{ t('memoryUsage') }}</p>
          <p class="text-2xl font-bold text-foreground">
            {{ data ? formatBytes(data.mem_used, 1) : '-' }}
            <span class="text-sm font-normal text-muted-foreground">
              / {{ data ? formatBytes(data.mem_total, 1) : '-' }}
            </span>
          </p>
          <div class="mt-2 h-1.5 overflow-hidden rounded-full bg-muted">
            <div
              class="h-full rounded-full bg-primary transition-[width]"
              :style="{ width: `${memPercent}%` }"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
