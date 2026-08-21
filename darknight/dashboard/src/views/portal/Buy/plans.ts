export type PlanFilter = 'all' | 'period' | 'traffic'
export type PlanCategory = 'period' | 'traffic'
export type BillingCycleId = 'monthly' | 'quarterly' | 'yearly' | 'two_years'

export interface BillingCycle {
  id: BillingCycleId
  labelKey: string
  price: number
}

export interface Plan {
  id: string
  name: string
  category: PlanCategory
  trafficLabelKey: string
  featureKeys: string[]
  cycles: BillingCycle[]
  /** 卡片主价格展示的周期（列表页用） */
  displayCycleId: BillingCycleId
}

export const PLANS: Plan[] = [
  {
    id: '100g',
    name: '100G',
    category: 'period',
    trafficLabelKey: 'portal.buy.feature.traffic100',
    displayCycleId: 'yearly',
    featureKeys: [
      'portal.buy.feature.traffic100',
      'portal.buy.feature.regions',
      'portal.buy.feature.bandwidth100',
      'portal.buy.feature.singleUser',
      'portal.buy.feature.selfConfig',
      'portal.buy.feature.yearlyPrice',
      'portal.buy.feature.twoYearPrice'
    ],
    cycles: [
      { id: 'yearly', labelKey: 'portal.buy.cycle.yearly', price: 12 },
      { id: 'two_years', labelKey: 'portal.buy.cycle.twoYears', price: 20 }
    ]
  },
  {
    id: '1024g',
    name: '1024G',
    category: 'traffic',
    trafficLabelKey: 'portal.buy.feature.traffic1024',
    displayCycleId: 'quarterly',
    featureKeys: [
      'portal.buy.feature.traffic1024',
      'portal.buy.feature.regions',
      'portal.buy.feature.bandwidth5g',
      'portal.buy.feature.singleUser',
      'portal.buy.feature.selfConfig'
    ],
    cycles: [{ id: 'quarterly', labelKey: 'portal.buy.cycle.quarterly', price: 15 }]
  },
  {
    id: '2048g',
    name: '2048G',
    category: 'traffic',
    trafficLabelKey: 'portal.buy.feature.traffic2048',
    displayCycleId: 'monthly',
    featureKeys: [
      'portal.buy.feature.traffic2048',
      'portal.buy.feature.regions',
      'portal.buy.feature.bandwidth10g',
      'portal.buy.feature.singleUser',
      'portal.buy.feature.selfConfig'
    ],
    cycles: [{ id: 'monthly', labelKey: 'portal.buy.cycle.monthly', price: 7 }]
  }
]

export const PAYMENT_METHODS = [
  { id: 'alipay_1', labelKey: 'portal.buy.payment.alipay1' },
  { id: 'alipay_bank', labelKey: 'portal.buy.payment.alipayBank' },
  { id: 'wechat_2', labelKey: 'portal.buy.payment.wechat2' }
] as const

export type PaymentMethodId = (typeof PAYMENT_METHODS)[number]['id']

export function getPlanById(id: string): Plan | undefined {
  return PLANS.find((plan) => plan.id === id)
}

export function getCycle(plan: Plan, cycleId: BillingCycleId): BillingCycle | undefined {
  return plan.cycles.find((cycle) => cycle.id === cycleId)
}

export function formatPrice(amount: number): string {
  return amount.toFixed(2)
}

export function filterPlans(filter: PlanFilter): Plan[] {
  if (filter === 'all') return PLANS
  return PLANS.filter((plan) => plan.category === filter)
}
