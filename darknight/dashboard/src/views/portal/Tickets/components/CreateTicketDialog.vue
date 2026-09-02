<script setup lang="ts">
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useMutation } from '@tanstack/vue-query'
import { Loader2 } from 'lucide-vue-next'
import { toast } from 'vue-sonner'
import { createPortalTicket, type CreateTicketBody, type TicketPriority } from '@/api/portal/tickets'
import { resolvePortalApiError } from '@/utils/portalError'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from '@/components/ui/select'

const props = defineProps<{ modelValue: boolean }>()
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  created: []
}>()

const { t } = useI18n()

const subject = ref('')
const priority = ref<TicketPriority>('normal')
const content = ref('')

const PRIORITIES: TicketPriority[] = ['low', 'normal', 'high', 'urgent']

const createMutation = useMutation({
  mutationFn: (body: CreateTicketBody) => createPortalTicket(body)
})

function resetForm() {
  subject.value = ''
  priority.value = 'normal'
  content.value = ''
}

watch(
  () => props.modelValue,
  (open) => {
    if (open) resetForm()
  }
)

function close() {
  emit('update:modelValue', false)
}

async function onSubmit() {
  const trimmedSubject = subject.value.trim()
  const trimmedContent = content.value.trim()
  if (!trimmedSubject) {
    toast.error(t('portal.tickets.subjectRequired'))
    return
  }
  if (!trimmedContent) {
    toast.error(t('portal.tickets.contentRequired'))
    return
  }
  try {
    await createMutation.mutateAsync({
      subject: trimmedSubject,
      priority: priority.value,
      content: trimmedContent
    })
    toast.success(t('portal.tickets.createSuccess'))
    resetForm()
    emit('created')
    close()
  } catch (err) {
    toast.error(resolvePortalApiError(err, t))
  }
}
</script>

<template>
  <Dialog :open="modelValue" @update:open="emit('update:modelValue', $event)">
    <DialogContent class="flex max-h-[90vh] flex-col sm:max-w-2xl">
      <DialogHeader>
        <DialogTitle>{{ t('portal.tickets.createTitle') }}</DialogTitle>
      </DialogHeader>

      <div class="space-y-4 py-2">
        <div class="space-y-1">
          <Label class="text-xs text-muted-foreground" for="ticket-subject">
            {{ t('portal.tickets.subject') }}
          </Label>
          <Input
            id="ticket-subject"
            v-model="subject"
            :placeholder="t('portal.tickets.subjectPlaceholder')"
          />
        </div>

        <div class="space-y-1">
          <Label class="text-xs text-muted-foreground">{{ t('portal.tickets.priority') }}</Label>
          <Select v-model="priority">
            <SelectTrigger class="w-full sm:w-[200px]">
              <SelectValue :placeholder="t('portal.tickets.priorityPlaceholder')" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem v-for="p in PRIORITIES" :key="p" :value="p">
                {{ t(`portal.tickets.priority.${p}`) }}
              </SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div class="space-y-1">
          <Label class="text-xs text-muted-foreground" for="ticket-content">
            {{ t('portal.tickets.message') }}
          </Label>
          <textarea
            id="ticket-content"
            v-model="content"
            rows="5"
            :placeholder="t('portal.tickets.messagePlaceholder')"
            class="w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm text-foreground shadow-xs outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
          />
        </div>
      </div>

      <DialogFooter>
        <Button type="button" variant="outline" @click="close">
          {{ t('cancel') }}
        </Button>
        <Button type="button" :disabled="createMutation.isPending.value" @click="onSubmit">
          <Loader2 v-if="createMutation.isPending.value" class="mr-2 size-4 animate-spin" />
          {{ t('confirm') }}
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
