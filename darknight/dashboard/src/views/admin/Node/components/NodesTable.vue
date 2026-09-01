<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { Pencil, RefreshCw, Trash2 } from 'lucide-vue-next'
import type { NodeStatus, NodeType } from '@/api/node/types'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'

defineProps<{ nodes: NodeType[]; loading: boolean }>()
const emit = defineEmits<{
  edit: [node: NodeType]
  remove: [node: NodeType]
  reconnect: [node: NodeType]
}>()

const { t } = useI18n()

const STATUS_VARIANT: Record<
  NodeStatus,
  'default' | 'secondary' | 'outline' | 'destructive'
> = {
  connected: 'default',
  connecting: 'outline',
  error: 'destructive',
  disabled: 'secondary'
}

function statusVariant(status?: NodeStatus | null) {
  return status ? STATUS_VARIANT[status] : 'secondary'
}
</script>

<template>
  <div class="overflow-x-auto rounded-xl border border-border bg-card">
    <div v-if="loading && !nodes.length" class="space-y-3 p-4">
      <Skeleton v-for="i in 5" :key="i" class="h-10 w-full" />
    </div>

    <div
      v-else-if="!nodes.length"
      class="flex flex-col items-center gap-3 px-4 py-10 text-center text-muted-foreground"
    >
      <p class="text-sm">{{ t('nodes.title') }}</p>
    </div>

    <table v-else class="w-full min-w-[720px] text-sm">
      <thead class="border-b border-border text-muted-foreground">
        <tr>
          <th class="px-4 py-3 text-start font-medium">{{ t('nodes.nodeName') }}</th>
          <th class="px-4 py-3 text-start font-medium">{{ t('nodes.nodeAddress') }}</th>
          <th class="px-4 py-3 text-start font-medium">{{ t('nodes.nodePort') }}</th>
          <th class="px-4 py-3 text-start font-medium">{{ t('nodes.nodeAPIPort') }}</th>
          <th class="px-4 py-3 text-start font-medium">Xray</th>
          <th class="px-4 py-3 text-start font-medium">{{ t('usersTable.status') }}</th>
          <th class="px-4 py-3 text-end font-medium" />
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="row in nodes"
          :key="row.id ?? row.name"
          class="border-b border-border last:border-0"
        >
          <td class="px-4 py-3 text-foreground">{{ row.name }}</td>
          <td class="px-4 py-3 text-foreground">{{ row.address }}</td>
          <td class="px-4 py-3 text-foreground">{{ row.port }}</td>
          <td class="px-4 py-3 text-foreground">{{ row.api_port }}</td>
          <td class="px-4 py-3 text-muted-foreground">{{ row.xray_version || '-' }}</td>
          <td class="px-4 py-3">
            <Badge
              :variant="statusVariant(row.status)"
              :title="row.message || undefined"
            >
              {{ t(`nodeModal.status.${row.status || 'disabled'}`) }}
            </Badge>
          </td>
          <td class="px-4 py-3 text-end">
            <div class="inline-flex items-center gap-1">
              <Button
                variant="ghost"
                size="icon"
                type="button"
                :title="t('nodes.reconnect')"
                @click="emit('reconnect', row)"
              >
                <RefreshCw class="size-4" />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                type="button"
                @click="emit('edit', row)"
              >
                <Pencil class="size-4" />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                type="button"
                @click="emit('remove', row)"
              >
                <Trash2 class="size-4 text-destructive" />
              </Button>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
