import type { MaybeRefOrGetter } from 'vue'
import { computed, toValue } from 'vue'
import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { http } from '@/config/axios'
import type {
  TicketDetail,
  TicketListItem,
  TicketPriority,
  TicketStatus
} from '@/api/portal/tickets'

export interface AdminTicketListItem extends TicketListItem {
  username: string
}

export interface TicketFilters {
  status?: TicketStatus | ''
  priority?: TicketPriority | ''
  offset?: number
  limit?: number
}

export const ticketsQueryKey = ['admin', 'tickets'] as const

export function useTicketsQuery(filters: MaybeRefOrGetter<TicketFilters>) {
  return useQuery({
    queryKey: computed(() => [...ticketsQueryKey, toValue(filters)]),
    queryFn: () => {
      const f = toValue(filters)
      const query: Record<string, string | number> = {}
      if (f.status) query.status = f.status
      if (f.priority) query.priority = f.priority
      if (f.offset != null) query.offset = f.offset
      if (f.limit != null) query.limit = f.limit
      return http<AdminTicketListItem[]>('/admin/tickets', { query })
    },
    refetchOnWindowFocus: false
  })
}

export function useTicketMutations() {
  const queryClient = useQueryClient()
  const invalidate = () => queryClient.invalidateQueries({ queryKey: ticketsQueryKey })

  const replyTicket = useMutation({
    mutationFn: ({ id, content }: { id: number; content: string }) =>
      http<TicketDetail>(`/admin/tickets/${id}/replies`, { method: 'POST', body: { content } }),
    onSuccess: invalidate
  })

  const updateTicket = useMutation({
    mutationFn: ({
      id,
      body
    }: {
      id: number
      body: { status?: TicketStatus; priority?: TicketPriority }
    }) => http<TicketDetail>(`/admin/tickets/${id}`, { method: 'PATCH', body }),
    onSuccess: invalidate
  })

  const fetchTicketDetail = (id: number) => http<TicketDetail>(`/admin/tickets/${id}`)

  return { replyTicket, updateTicket, fetchTicketDetail }
}
