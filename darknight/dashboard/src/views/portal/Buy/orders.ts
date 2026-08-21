import type { BillingCycleId, PaymentMethodId } from './plans'
import { getCycle, getPlanById } from './plans'

export type OrderStatus = 'pending' | 'paid' | 'closed'

export interface PortalOrder {
  id: string
  planId: string
  cycleId: BillingCycleId
  amount: number
  status: OrderStatus
  paymentMethod?: PaymentMethodId
  coupon?: string
  createdAt: string
}

const STORAGE_KEY = 'portal_orders'

function readOrders(): Record<string, PortalOrder> {
  try {
    return JSON.parse(sessionStorage.getItem(STORAGE_KEY) || '{}') as Record<string, PortalOrder>
  } catch {
    return {}
  }
}

function writeOrders(orders: Record<string, PortalOrder>) {
  sessionStorage.setItem(STORAGE_KEY, JSON.stringify(orders))
}

function generateOrderId(): string {
  const now = new Date()
  const pad = (n: number, len = 2) => String(n).padStart(len, '0')
  return (
    `${now.getFullYear()}${pad(now.getMonth() + 1)}${pad(now.getDate())}` +
    `${pad(now.getHours())}${pad(now.getMinutes())}${pad(now.getSeconds())}` +
    `${Math.floor(Math.random() * 1_000_000_000_000)
      .toString()
      .padStart(12, '0')}`
  )
}

export function createOrder(planId: string, cycleId: BillingCycleId, coupon?: string): PortalOrder {
  const plan = getPlanById(planId)
  const cycle = plan ? getCycle(plan, cycleId) : undefined
  if (!plan || !cycle) {
    throw new Error('Invalid plan or billing cycle')
  }

  const order: PortalOrder = {
    id: generateOrderId(),
    planId,
    cycleId,
    amount: cycle.price,
    status: 'pending',
    coupon: coupon?.trim() || undefined,
    createdAt: new Date().toISOString()
  }

  const orders = readOrders()
  orders[order.id] = order
  writeOrders(orders)
  return order
}

export function getOrder(orderId: string): PortalOrder | undefined {
  return readOrders()[orderId]
}

export function updateOrder(orderId: string, patch: Partial<PortalOrder>): PortalOrder | undefined {
  const orders = readOrders()
  const current = orders[orderId]
  if (!current) return undefined
  const next = { ...current, ...patch }
  orders[orderId] = next
  writeOrders(orders)
  return next
}

export function closeOrder(orderId: string): PortalOrder | undefined {
  return updateOrder(orderId, { status: 'closed' })
}

export function formatOrderTime(iso: string): string {
  const date = new Date(iso)
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`
}
