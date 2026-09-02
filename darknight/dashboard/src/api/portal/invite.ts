import { http } from '@/config/axios'

export interface InviteSummary {
  balance: number
  currency: string
  registered_count: number
  commission_rate: number
  pending_commission: number
  total_commission: number
}

export interface InviteCode {
  code: string
  created_at: string
  invite_url: string
}

export interface InvitePayout {
  paid_at: string
  amount: number
  currency: string
}

export function fetchInviteSummary() {
  return http<InviteSummary>('/invite/summary')
}

export function fetchInviteCodes() {
  return http<InviteCode[]>('/invite/codes')
}

export function generateInviteCode() {
  return http<InviteCode>('/invite/codes', { method: 'POST' })
}

export function fetchInvitePayouts() {
  return http<InvitePayout[]>('/invite/payouts')
}

export function formatInviteTime(iso: string): string {
  const date = new Date(iso)
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${date.getFullYear()}/${pad(date.getMonth() + 1)}/${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}`
}
