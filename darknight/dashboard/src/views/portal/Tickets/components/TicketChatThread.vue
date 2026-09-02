<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { formatTicketTime, type TicketReply } from '@/api/portal/tickets'
import { cn } from '@/lib/utils'

const props = defineProps<{
  replies: TicketReply[]
  perspective: 'user' | 'admin'
  username?: string
}>()

const { t } = useI18n()

function isOwn(reply: TicketReply) {
  return props.perspective === 'user'
    ? reply.author_type === 'user'
    : reply.author_type === 'admin'
}

function authorLabel(reply: TicketReply) {
  if (reply.author_type === 'admin') {
    return t('portal.tickets.authorAdmin')
  }
  if (props.perspective === 'admin' && props.username) {
    return props.username
  }
  return t('portal.tickets.authorUser')
}
</script>

<template>
  <div
    class="flex min-h-[220px] max-h-[360px] flex-col gap-3 overflow-y-auto rounded-xl bg-muted/30 p-4"
  >
    <div
      v-for="reply in replies"
      :key="reply.id"
      class="flex"
      :class="isOwn(reply) ? 'justify-end' : 'justify-start'"
    >
      <div
        :class="
          cn(
            'max-w-[78%] rounded-2xl px-4 py-2.5 shadow-sm',
            isOwn(reply)
              ? 'rounded-br-md bg-primary text-primary-foreground'
              : 'rounded-bl-md border border-border bg-card text-foreground'
          )
        "
      >
        <div
          class="mb-1 flex items-center justify-between gap-3 text-[11px]"
          :class="isOwn(reply) ? 'text-primary-foreground/75' : 'text-muted-foreground'"
        >
          <span class="font-medium">{{ authorLabel(reply) }}</span>
          <span>{{ formatTicketTime(reply.created_at) }}</span>
        </div>
        <p class="whitespace-pre-wrap text-sm leading-relaxed">{{ reply.content }}</p>
      </div>
    </div>
  </div>
</template>
