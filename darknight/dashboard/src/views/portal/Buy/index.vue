<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { Check } from 'lucide-vue-next'
import { currencySymbol, formatPrice, type PlanFilter } from './plans'
import { usePlanCatalog, type PricedPlan } from './usePlanCatalog'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Skeleton } from '@/components/ui/skeleton'
import { cn } from '@/lib/utils'

const { t } = useI18n()
const router = useRouter()

const activeFilter = ref<PlanFilter>('all')
const { currency, filterPlans, isLoading, isError } = usePlanCatalog()

const filters: { id: PlanFilter; labelKey: string }[] = [
  { id: 'all', labelKey: 'portal.buy.filter.all' },
  { id: 'period', labelKey: 'portal.buy.filter.period' },
  { id: 'traffic', labelKey: 'portal.buy.filter.traffic' }
]

const plans = computed(() => filterPlans(activeFilter.value))

function displayCycle(plan: PricedPlan) {
  return plan.cycles.find((cycle) => cycle.id === plan.displayCycleId) ?? plan.cycles[0]
}

function subscribe(planId: string) {
  router.push({ name: 'portal-buy-configure', params: { planId } })
}
</script>

<template>
  <div class="max-w-6xl">
    <h2 class="mb-5 text-2xl font-bold tracking-tight text-foreground">
      {{ t('portal.buy.choosePlan') }}
    </h2>

    <div class="mb-6 inline-flex rounded-lg bg-muted p-1">
      <button
        v-for="item in filters"
        :key="item.id"
        type="button"
        :class="
          cn(
            'rounded-md px-4 py-1.5 text-sm font-medium transition-colors',
            activeFilter === item.id
              ? 'bg-background text-foreground shadow-sm'
              : 'text-muted-foreground hover:text-foreground'
          )
        "
        @click="activeFilter = item.id"
      >
        {{ t(item.labelKey) }}
      </button>
    </div>

    <Alert v-if="isError" variant="destructive" class="mb-4">
      <AlertDescription>{{ t('portal.buy.plansLoadFailed') }}</AlertDescription>
    </Alert>

    <div v-if="isLoading" class="grid gap-5 lg:grid-cols-3">
      <Skeleton v-for="i in 3" :key="i" class="h-96 rounded-xl" />
    </div>

    <div v-else class="grid items-stretch gap-5 lg:grid-cols-3">
      <div
        v-for="plan in plans"
        :key="plan.id"
        class="flex flex-col rounded-xl border border-border bg-card p-7 transition-shadow hover:shadow-lg"
      >
        <p class="text-2xl font-bold text-foreground">{{ plan.name }}</p>
        <div class="mt-3 flex items-baseline gap-1">
          <span class="text-lg font-semibold text-foreground">{{ currencySymbol(currency) }}</span>
          <span class="text-4xl font-bold leading-none tracking-tight text-foreground">
            {{ formatPrice(displayCycle(plan).price) }}
          </span>
          <span class="text-sm text-muted-foreground">{{ t(displayCycle(plan).labelKey) }}</span>
        </div>
        <ul class="mt-6 flex-1 space-y-2.5">
          <li
            v-for="key in plan.featureKeys"
            :key="key"
            class="flex items-start gap-2 text-sm leading-relaxed text-muted-foreground"
          >
            <Check class="mt-0.5 size-4 shrink-0 text-primary" />
            <span>{{ t(key) }}</span>
          </li>
        </ul>
        <Button class="mt-7 h-11 w-full" @click="subscribe(plan.id)">
          {{ t('portal.buy.subscribeNow') }}
        </Button>
      </div>
    </div>
  </div>
</template>
