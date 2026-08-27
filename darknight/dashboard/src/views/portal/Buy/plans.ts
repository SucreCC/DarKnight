export type PlanFilter = 'all' | 'period' | 'traffic'
export type PlanCategory = 'period' | 'traffic'
export type BillingCycleId = 'monthly' | 'quarterly' | 'yearly' | 'two_years'

/**
 * 套餐的展示文案。价格与额度是后端 `/plans` 的权威数据，这里不保存任何金额，
 * 避免前后端各存一份导致改价漏改。
 */
export interface PlanMeta {
  id: string
  name: string
  category: PlanCategory
  featureKeys: string[]
  /** 卡片主价格展示的周期（列表页用） */
  displayCycleId: BillingCycleId
}

export const CYCLE_LABEL_KEYS: Record<BillingCycleId, string> = {
  monthly: 'portal.buy.cycle.monthly',
  quarterly: 'portal.buy.cycle.quarterly',
  yearly: 'portal.buy.cycle.yearly',
  two_years: 'portal.buy.cycle.twoYears'
}

export const PLAN_META: PlanMeta[] = [
  {
    id: '100g',
    name: '100G',
    category: 'period',
    displayCycleId: 'yearly',
    featureKeys: [
      'portal.buy.feature.traffic100',
      'portal.buy.feature.regions',
      'portal.buy.feature.bandwidth100',
      'portal.buy.feature.singleUser',
      'portal.buy.feature.selfConfig'
    ]
  },
  {
    id: '1024g',
    name: '1024G',
    category: 'traffic',
    displayCycleId: 'quarterly',
    featureKeys: [
      'portal.buy.feature.traffic1024',
      'portal.buy.feature.regions',
      'portal.buy.feature.bandwidth5g',
      'portal.buy.feature.singleUser',
      'portal.buy.feature.selfConfig'
    ]
  },
  {
    id: '2048g',
    name: '2048G',
    category: 'traffic',
    displayCycleId: 'monthly',
    featureKeys: [
      'portal.buy.feature.traffic2048',
      'portal.buy.feature.regions',
      'portal.buy.feature.bandwidth10g',
      'portal.buy.feature.singleUser',
      'portal.buy.feature.selfConfig'
    ]
  }
]

export function getPlanMeta(id: string): PlanMeta | undefined {
  return PLAN_META.find((plan) => plan.id === id)
}

export function getCycleLabelKey(cycleId: string): string {
  return CYCLE_LABEL_KEYS[cycleId as BillingCycleId] ?? cycleId
}

export function formatPrice(amount: number): string {
  return amount.toFixed(2)
}

export function currencySymbol(currency: string): string {
  return currency === 'USD' ? '$' : `${currency} `
}
