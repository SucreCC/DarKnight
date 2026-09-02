<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { Loader2 } from 'lucide-vue-next'
import { toast } from 'vue-sonner'
import { useTicketMutations } from '@/api/ticket'
import type { AdminTicketListItem } from '@/api/ticket'
import {
  formatTicketTime,
  type TicketDetail,
  type TicketPriority,
  type TicketStatus
} from '@/api/portal/tickets'
import { extractErrorDetail } from '@/config/axios'
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from '@/components/ui/select'

const props = defineProps<{
  modelValue: boolean
  ticketRow: AdminTicketListItem | null
}>()
const emit = defineEmits<{ 'update:modelValue': [value: boolean] }>()

const { t } = useI18n()
const { fetchTicketDetail, replyTicket, updateTicket } = useTicketMutations()

const detail = ref<TicketDetail | null>(null)
const loading = ref(false)
const replyContent = ref('')
const status = ref<TicketStatus>('open')
const priority = ref<TicketPriority>('normal')

const STATUSES: TicketStatus[] = ['open', 'pending', 'resolved', 'closed']
const PRIORITIES: TicketPriority[] = ['low', 'normal', 'high', 'urgent']

const isClosed = computed(() => detail.value?.status === 'closed')

async function loadDetail() {
  if (!props.ticketRow) return
  loading.value = true
  try {
    detail.value = await fetchTicketDetail(props.ticketRow.id)
    status.value = detail.value.status
    priority.value = detail.value.priority
  } catch (err: unknown) {
    const msg = extractErrorDetail(err)
    toast.error(typeof msg === 'string' ? msg : t('portal.requestFailed'))
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

async function onStatusChange(value: unknown) {
  if (!detail.value || typeof value !== 'string') return
  const next = value as TicketStatus
  if (next === detail.value.status) return
  try {
    detail.value = await updateTicket.mutateAsync({
      id: detail.value.id,
      body: { status: next }
    })
    status.value = detail.value.status
    toast.success(t('admin.tickets.updateSuccess'))
  } catch (err: unknown) {
    const msg = extractErrorDetail(err)
    toast.error(typeof msg === 'string' ? msg : t('portal.requestFailed'))
    status.value = detail.value?.status ?? status.value
  }
}

async function onPriorityChange(value: unknown) {
  if (!detail.value || typeof value !== 'string') return
  const next = value as TicketPriority
  if (next === detail.value.priority) return
  try {
    detail.value = await updateTicket.mutateAsync({
      id: detail.value.id,
      body: { priority: next }
    })
    priority.value = detail.value.priority
    toast.success(t('admin.tickets.updateSuccess'))
  } catch (err: unknown) {
    const msg = extractErrorDetail(err)
    toast.error(typeof msg === 'string' ? msg : t('portal.requestFailed'))
    priority.value = detail.value?.priority ?? priority.value
  }
}

async function onReply() {
  if (!detail.value) return
  const content = replyContent.value.trim()
  if (!content) return
  try {
    detail.value = await replyTicket.mutateAsync({ id: detail.value.id, content })
    replyContent.value = ''
    status.value = detail.value.status
    toast.success(t('portal.tickets.replySuccess'))
  } catch (err: unknown) {
    const msg = extractErrorDetail(err)
    toast.error(typeof msg === 'string' ? msg : t('portal.requestFailed'))
  }
}

async function quickStatus(next: TicketStatus) {
  if (!detail.value) return
  try {
    detail.value = await updateTicket.mutateAsync({
      id: detail.value.id,
      body: { status: next }
    })
    status.value = detail.value.status
    toast.success(t('admin.tickets.updateSuccess'))
  } catch (err: unknown) {
    const msg = extractErrorDetail(err)
    toast.error(typeof msg === 'string' ? msg : t('portal.requestFailed'))
  }
}
</script>

<template>
  <Dialog :open="modelValue" @update:open="emit('update:modelValue', $event)">
    <DialogContent class="flex max-h-[90vh] flex-col sm:max-w-2xl">
      <DialogHeader>
        <DialogTitle>{{ detail?.subject ?? t('admin.tickets.handle') }}</DialogTitle>
      </DialogHeader>

      <div v-if="loading" class="flex items-center justify-center py-12 text-muted-foreground">
        <Loader2 class="size-6 animate-spin" />
      </div>

      <template v-else-if="detail">
        <div class="flex flex-wrap items-center gap-3 border-b border-border pb-4">
          <div class="space-y-1">
            <Label class="text-xs text-muted-foreground">{{ t('portal.tickets.statusLabel') }}</Label>
            <Select :model-value="status" @update:model-value="onStatusChange">
              <SelectTrigger class="w-[140px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem v-for="s in STATUSES" :key="s" :value="s">
                  {{ t(`portal.tickets.status.${s}`) }}
                </SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div class="space-y-1">
            <Label class="text-xs text-muted-foreground">{{ t('portal.tickets.priority') }}</Label>
            <Select :model-value="priority" @update:model-value="onPriorityChange">
              <SelectTrigger class="w-[140px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem v-for="p in PRIORITIES" :key="p" :value="p">
                  {{ t(`portal.tickets.priority.${p}`) }}
                </SelectItem>
              </SelectContent>
            </Select>
          </div>
          <Badge v-if="ticketRow" variant="outline">{{ ticketRow.username }}</Badge>
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
              :disabled="replyTicket.isPending.value || !replyContent.trim()"
              @click="onReply"
            >
              <Loader2 v-if="replyTicket.isPending.value" class="mr-2 size-4 animate-spin" />
              {{ t('portal.tickets.sendReply') }}
            </Button>
            <Button
              v-if="detail.status !== 'resolved'"
              type="button"
              variant="outline"
              @click="quickStatus('resolved')"
            >
              {{ t('admin.tickets.markResolved') }}
            </Button>
            <Button
              v-if="detail.status !== 'closed'"
              type="button"
              variant="outline"
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
