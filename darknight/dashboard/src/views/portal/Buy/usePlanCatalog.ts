import { computed } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { fetchPlanCatalog } from '@/api/portal/orders'
import {
  PLAN_META,
  getCycleLabelKey,
  getPlanMeta,
  type BillingCycleId,
  type PlanFilter,
  type PlanMeta
} from './plans'

export interface PricedCycle {
  id: BillingCycleId
  labelKey: string
  price: number
  dataLimitGb: number
  durationDays: number
}

export interface PricedPlan extends PlanMeta {
  cycles: PricedCycle[]
}

export const planCatalogQueryKey = ['portal', 'plans'] as const

/** 套餐展示数据：文案取自本地 i18n，价格与额度一律来自后端 `/plans`。 */
export function usePlanCatalog() {
  const query = useQuery({
    queryKey: planCatalogQueryKey,
    queryFn: fetchPlanCatalog,
    staleTime: 5 * 60 * 1000,
    refetchOnWindowFocus: false
  })

  const currency = computed(() => query.data.value?.currency ?? 'USD')

  const plans = computed<PricedPlan[]>(() => {
    const catalog = query.data.value
    if (!catalog) return []

    const byId = new Map(catalog.plans.map((plan) => [plan.plan_id, plan]))
    return PLAN_META.flatMap((meta) => {
      const priced = byId.get(meta.id)
      if (!priced?.cycles.length) return []
      return [
        {
          ...meta,
          cycles: priced.cycles.map((cycle) => ({
            id: cycle.cycle_id as BillingCycleId,
            labelKey: getCycleLabelKey(cycle.cycle_id),
            price: cycle.price,
            dataLimitGb: cycle.data_limit_gb,
            durationDays: cycle.duration_days
          }))
        }
      ]
    })
  })

  function getPlan(planId: string): PricedPlan | undefined {
    return plans.value.find((plan) => plan.id === planId)
  }

  function getCycle(planId: string, cycleId: string): PricedCycle | undefined {
    return getPlan(planId)?.cycles.find((cycle) => cycle.id === cycleId)
  }

  function filterPlans(filter: PlanFilter): PricedPlan[] {
    if (filter === 'all') return plans.value
    return plans.value.filter((plan) => plan.category === filter)
  }

  return {
    plans,
    currency,
    isLoading: query.isLoading,
    isError: query.isError,
    getPlan,
    getCycle,
    filterPlans,
    hasMeta: (planId: string) => Boolean(getPlanMeta(planId))
  }
}
