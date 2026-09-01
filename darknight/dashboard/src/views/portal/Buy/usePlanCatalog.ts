import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useQuery } from '@tanstack/vue-query'
import { fetchPlanCatalog } from '@/api/portal/orders'
import { pickLocale, type PlanCategory, type PlanFilter } from './plans'

export interface PricedCycle {
  id: string
  label: string
  price: number
  dataLimitGb: number
  durationDays: number
}

export interface PricedPlan {
  id: string
  name: string
  category: PlanCategory
  features: string[]
  displayCycleId: string
  sortOrder: number
  cycles: PricedCycle[]
}

export const planCatalogQueryKey = ['portal', 'plans'] as const

/** 套餐展示数据完全来自后端 `/plans`（含中英文案）。 */
export function usePlanCatalog() {
  const { locale } = useI18n()
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

    const loc = locale.value
    return [...catalog.plans]
      .sort((a, b) => a.sort_order - b.sort_order)
      .map((plan) => ({
        id: plan.plan_id,
        name: pickLocale(loc, plan.name_zh, plan.name_en),
        category: plan.category,
        features: pickLocale(loc, plan.features_zh, plan.features_en),
        displayCycleId: plan.display_cycle_id,
        sortOrder: plan.sort_order,
        cycles: plan.cycles.map((cycle) => ({
          id: cycle.cycle_id,
          label: pickLocale(loc, cycle.label_zh, cycle.label_en),
          price: cycle.price,
          dataLimitGb: cycle.data_limit_gb,
          durationDays: cycle.duration_days
        }))
      }))
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
    filterPlans
  }
}
