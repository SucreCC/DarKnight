<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useMutation, useQueryClient } from '@tanstack/vue-query'
import { Loader2 } from 'lucide-vue-next'
import { toast } from 'vue-sonner'
import {
  fetchPortalTicket,
  formatTicketTime,
  replyPortalTicket,
  updatePortalTicketStatus,
  type TicketDetail,
  type TicketListItem,
  type TicketPriority,
  type TicketStatus
} from '@/api/portal/tickets'
import { resolvePortalApiError } from '@/utils/portalError'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle
} from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'

const props = defineProps<{
  modelValue: boolean
  ticketRow: TicketListItem | null
}>()
const emit = defineEmits<{ 'update:modelValue': [value: boolean] }>()

const { t } = useI18n()
const queryClient = useQueryClient()

const detail = ref<TicketDetail | null>(null)
const loading = ref(false)
const replyContent = ref('')

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

const isClosed = computed(() => detail.value?.status === 'closed')

const replyMutation = useMutation({
  mutationFn: ({ id, content }: { id: number; content: string }) =>
    replyPortalTicket(id, content)
})

const statusMutation = useMutation({
  mutationFn: ({ id, status }: { id: number; status: TicketStatus }) =>
    updatePortalTicketStatus(id, status)
})

function invalidate() {
  queryClient.invalidateQueries({ queryKey: ['portal', 'tickets'] })
  if (detail.value) {
    queryClient.invalidateQueries({ queryKey: ['portal', 'ticket', detail.value.id] })
  }
}

async function loadDetail() {
  if (!props.ticketRow) return
  loading.value = true
  try {
    detail.value = await fetchPortalTicket(props.ticketRow.id)
  } catch (err) {
    toast.error(resolvePortalApiError(err, t))
    emit('update:modelValue', false)
  } finally {
    loading.value = false
  }
}

watch(
  () => props.modelValue,
  (open) => {
    if (open) {
      replyContent.value = ''
      loadDetail()
    } else {
      detail.value = null
    }
  }
)

async function onReply() {
  if (!detail.value) return
  const content = replyContent.value.trim()
  if (!content) return
  try {
    detail.value = await replyMutation.mutateAsync({ id: detail.value.id, content })
    replyContent.value = ''
    invalidate()
    toast.success(t('portal.tickets.replySuccess'))
  } catch (err) {
    toast.error(resolvePortalApiError(err, t))
  }
}

async function quickStatus(next: TicketStatus) {
  if (!detail.value) return
  try {
    detail.value = await statusMutation.mutateAsync({ id: detail.value.id, status: next })
    invalidate()
    toast.success(
      next === 'closed' ? t('portal.tickets.closeSuccess') : t('admin.tickets.updateSuccess')
    )
  } catch (err) {
    toast.error(resolvePortalApiError(err, t))
  }
}
</script>

<template>
  <Dialog :open="modelValue" @update:open="emit('update:modelValue', $event)">
    <DialogContent class="flex max-h-[90vh] flex-col sm:max-w-2xl">
      <DialogHeader>
        <DialogTitle>{{ detail?.subject ?? t('portal.tickets.detailTitle') }}</DialogTitle>
      </DialogHeader>

      <div v-if="loading" class="flex items-center justify-center py-12 text-muted-foreground">
        <Loader2 class="size-6 animate-spin" />
      </div>

      <template v-else-if="detail">
        <div class="flex flex-wrap items-center gap-3 border-b border-border pb-4">
          <div class="space-y-1">
            <Label class="text-xs text-muted-foreground">{{ t('portal.tickets.statusLabel') }}</Label>
            <Badge :variant="STATUS_VARIANT[detail.status]">
              {{ t(`portal.tickets.status.${detail.status}`) }}
            </Badge>
          </div>
          <div class="space-y-1">
            <Label class="text-xs text-muted-foreground">{{ t('portal.tickets.priority') }}</Label>
            <Badge :variant="PRIORITY_VARIANT[detail.priority]">
              {{ t(`portal.tickets.priority.${detail.priority}`) }}
            </Badge>
          </div>
        </div>

        <div class="min-h-0 flex-1 space-y-3 overflow-y-auto py-4">
          <div
            v-for="reply in detail.replies"
            :key="reply.id"
            class="rounded-lg border border-border px-4 py-3"
            :class="reply.author_type === 'admin' ? 'bg-muted/40' : 'bg-background'"
          >
            <div class="mb-2 flex items-center justify-between gap-2 text-xs text-muted-foreground">
              <span>
                {{
                  reply.author_type === 'admin'
                    ? t('portal.tickets.authorAdmin')
                    : t('portal.tickets.authorUser')
                }}
              </span>
              <span>{{ formatTicketTime(reply.created_at) }}</span>
            </div>
            <p class="whitespace-pre-wrap text-sm text-foreground">{{ reply.content }}</p>
          </div>
        </div>

        <div v-if="!isClosed" class="space-y-3 border-t border-border pt-4">
          <textarea
            v-model="replyContent"
            rows="3"
            :placeholder="t('portal.tickets.replyPlaceholder')"
            class="w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm text-foreground shadow-xs outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
          />
          <div class="flex flex-wrap gap-2">
            <Button
              type="button"
              :disabled="replyMutation.isPending.value || !replyContent.trim()"
              @click="onReply"
            >
              <Loader2 v-if="replyMutation.isPending.value" class="mr-2 size-4 animate-spin" />
              {{ t('portal.tickets.sendReply') }}
            </Button>
            <Button
              v-if="detail.status !== 'resolved'"
              type="button"
              variant="outline"
              :disabled="statusMutation.isPending.value"
              @click="quickStatus('resolved')"
            >
              {{ t('admin.tickets.markResolved') }}
            </Button>
            <Button
              v-if="detail.status !== 'closed'"
              type="button"
              variant="outline"
              :disabled="statusMutation.isPending.value"
              @click="quickStatus('closed')"
            >
              {{ t('admin.tickets.close') }}
            </Button>
          </div>
        </div>
      </template>

      <DialogFooter>
        <Button type="button" variant="outline" @click="emit('update:modelValue', false)">
          {{ t('cancel') }}
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
