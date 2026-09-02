import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useQuery } from '@tanstack/vue-query'
import { fetchPlanCatalog } from '@/api/portal/orders'
import { pickLocale } from './plans'

export interface PricedPlan {
  id: string
  name: string
  features: string[]
  price: number
  durationDays: number
  sortOrder: number
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
        features: pickLocale(loc, plan.features_zh, plan.features_en),
        price: plan.price,
        durationDays: plan.duration_days,
        sortOrder: plan.sort_order
      }))
  })

  function getPlan(planId: string): PricedPlan | undefined {
    return plans.value.find((plan) => plan.id === planId)
  }

  return {
    plans,
    currency,
    isLoading: query.isLoading,
    isError: query.isError,
    getPlan
  }
}
