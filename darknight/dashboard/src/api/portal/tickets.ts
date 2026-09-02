import { http } from '@/config/axios'

export type TicketPriority = 'low' | 'normal' | 'high' | 'urgent'
export type TicketStatus = 'open' | 'pending' | 'resolved' | 'closed'
export type TicketAuthorType = 'user' | 'admin'

export interface TicketReply {
  id: number
  author_type: TicketAuthorType
  content: string
  created_at: string
}

export interface TicketListItem {
  id: number
  subject: string
  priority: TicketPriority
  status: TicketStatus
  created_at: string
  last_reply_at: string | null
}

export interface TicketDetail extends TicketListItem {
  replies: TicketReply[]
}

export interface CreateTicketBody {
  subject: string
  priority: TicketPriority
  content: string
}

export function fetchPortalTickets() {
  return http<TicketListItem[]>('/tickets')
}

export function fetchPortalTicket(ticketId: number) {
  return http<TicketDetail>(`/tickets/${ticketId}`)
}

export function createPortalTicket(body: CreateTicketBody) {
  return http<TicketDetail>('/tickets', { method: 'POST', body })
}

export function replyPortalTicket(ticketId: number, content: string) {
  return http<TicketDetail>(`/tickets/${ticketId}/replies`, {
    method: 'POST',
    body: { content }
  })
}

export function updatePortalTicketStatus(ticketId: number, status: TicketStatus) {
  return http<TicketDetail>(`/tickets/${ticketId}`, {
    method: 'PATCH',
    body: { status }
  })
}

export function closePortalTicket(ticketId: number) {
  return updatePortalTicketStatus(ticketId, 'closed')
}

export function formatTicketTime(iso: string | null | undefined): string {
  if (!iso) return '—'
  const date = new Date(iso)
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}`
}
