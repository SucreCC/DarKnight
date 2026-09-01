import { http } from '@/config/axios'

export type OrderStatus = 'pending' | 'paid' | 'closed' | 'failed'

export interface PortalOrder {
  id: string
  plan_id: string
  cycle_id: string
  amount: number
  currency: string
  status: OrderStatus
  payment_provider: string
  paypal_order_id?: string | null
  coupon?: string | null
  discount: number
  created_at: string
  paid_at?: string | null
}

export interface CouponPreview {
  coupon: string
  currency: string
  original_amount: number
  discount: number
  amount: number
}

export function previewCoupon(body: { plan_id: string; cycle_id: string; coupon: string }) {
  return http<CouponPreview>('/coupons/preview', { method: 'POST', body })
}

export interface PayPalConfig {
  client_id: string
  currency: string
  enabled: boolean
}

export interface PlanCycle {
  cycle_id: string
  price: number
  data_limit_gb: number
  duration_days: number
  label_zh: string
  label_en: string
}

export interface Plan {
  plan_id: string
  name_zh: string
  name_en: string
  category: 'period' | 'traffic'
  features_zh: string[]
  features_en: string[]
  display_cycle_id: string
  sort_order: number
  cycles: PlanCycle[]
}

export interface PlanCatalog {
  currency: string
  plans: Plan[]
}

export function fetchPayPalConfig() {
  return http<PayPalConfig>('/payments/paypal/config')
}

export function fetchPlanCatalog() {
  return http<PlanCatalog>('/plans')
}

export function createPortalOrder(body: {
  plan_id: string
  cycle_id: string
  coupon?: string
}) {
  return http<PortalOrder>('/orders', { method: 'POST', body })
}

export function fetchPortalOrders() {
  return http<PortalOrder[]>('/orders')
}

export function fetchPortalOrder(orderId: string) {
  return http<PortalOrder>(`/orders/${orderId}`)
}

export function closePortalOrder(orderId: string) {
  return http<PortalOrder>(`/orders/${orderId}/close`, { method: 'POST' })
}

/** refresh 用于失败重试：丢弃已作废的 PayPal 订单，重新创建一个 */
export function preparePortalOrderPayment(orderId: string, options: { refresh?: boolean } = {}) {
  return http<PortalOrder>(`/orders/${orderId}/prepare-payment`, {
    method: 'POST',
    query: options.refresh ? { refresh: true } : undefined
  })
}

export function capturePortalOrder(orderId: string) {
  return http<{ order: PortalOrder; detail: string }>(`/orders/${orderId}/capture`, {
    method: 'POST'
  })
}

export function formatOrderTime(iso: string): string {
  const date = new Date(iso)
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`
}
