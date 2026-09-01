<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { Check, Crown } from 'lucide-vue-next'
import {
  billingMonths,
  currencySymbol,
  formatPrice,
  monthlyEquivalent,
  planDiscountByMonths
} from './plans'
import { usePlanCatalog, type PricedPlan } from './usePlanCatalog'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Skeleton } from '@/components/ui/skeleton'
import { cn } from '@/lib/utils'

const { t } = useI18n()
const router = useRouter()

const { plans, currency, isLoading, isError } = usePlanCatalog()

interface PlanCard {
  plan: PricedPlan
  price: number
  durationDays: number
  monthlyPrice: number
  discount: number
  featured: boolean
}

const planCards = computed<PlanCard[]>(() => {
  const sorted = [...plans.value].sort((a, b) => {
    const daysA = a.cycles[0]?.durationDays ?? 0
    const daysB = b.cycles[0]?.durationDays ?? 0
    return daysA - daysB
  })

  const anchor = sorted.find((plan) => (plan.cycles[0]?.durationDays ?? 0) <= 31) ?? sorted[0]
  const anchorMonthly = anchor?.cycles[0]?.price ?? 4.99

  return sorted
    .filter((plan) => plan.cycles[0])
    .map((plan) => {
      const cycle = plan.cycles[0]
      const months = billingMonths(cycle.durationDays)
      return {
        plan,
        price: cycle.price,
        durationDays: cycle.durationDays,
        monthlyPrice: monthlyEquivalent(cycle.price, cycle.durationDays),
        discount: planDiscountByMonths(months),
        featured: cycle.durationDays >= 365
      }
    })
})

function subscribe(planId: string, cycleId: string) {
  router.push({
    name: 'portal-buy-configure',
    params: { planId },
    query: { cycle: cycleId }
  })
}
</script>

<template>
  <div class="max-w-6xl">
    <h2 class="mb-5 text-2xl font-bold tracking-tight text-foreground">
      {{ t('portal.buy.choosePlan') }}
    </h2>

    <Alert v-if="isError" variant="destructive" class="mb-4">
      <AlertDescription>{{ t('portal.buy.plansLoadFailed') }}</AlertDescription>
    </Alert>

    <div v-if="isLoading" class="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
      <Skeleton v-for="i in 4" :key="i" class="h-[28rem] rounded-xl" />
    </div>

    <div v-else class="grid items-stretch gap-5 sm:grid-cols-2 lg:grid-cols-4">
      <div
        v-for="card in planCards"
        :key="card.plan.id"
        :class="
          cn(
            'relative flex flex-col rounded-xl border bg-card p-7 transition-shadow hover:shadow-lg',
            card.featured
              ? 'border-primary/40 shadow-md ring-1 ring-primary/20'
              : 'border-border'
          )
        "
      >
        <div
          v-if="card.featured"
          class="absolute -top-3 start-1/2 inline-flex -translate-x-1/2 items-center gap-1 rounded-full bg-amber-400 px-3 py-1 text-xs font-semibold text-amber-950"
        >
          <Crown class="size-3.5" />
          {{ t('portal.buy.mostPopular') }}
        </div>

        <span
          :class="
            cn(
              'absolute end-4 top-8 inline-flex rounded-full px-3 py-1 text-xs font-medium',
              card.discount > 0
                ? 'bg-primary/10 text-primary'
                : 'bg-muted text-muted-foreground'
            )
          "
        >
          {{
            card.discount > 0
              ? t('portal.buy.discountBadge', { percent: card.discount })
              : t('portal.buy.noDiscount')
          }}
        </span>

        <p class="pe-24 text-2xl font-bold text-foreground">{{ card.plan.name }}</p>

        <div class="mt-4 flex items-baseline gap-1">
          <span class="text-lg font-semibold text-foreground">{{ currencySymbol(currency) }}</span>
          <span class="text-4xl font-bold leading-none tracking-tight text-foreground">
            {{ formatPrice(card.monthlyPrice) }}
          </span>
          <span class="text-sm text-muted-foreground">{{ t('portal.buy.perMonth') }}</span>
        </div>

        <ul v-if="card.plan.features.length" class="mt-5 flex-1 space-y-2">
          <li
            v-for="(feature, index) in card.plan.features"
            :key="index"
            class="flex items-start gap-2 text-sm leading-relaxed text-muted-foreground"
          >
            <Check class="mt-0.5 size-4 shrink-0 text-primary" />
            <span>{{ feature }}</span>
          </li>
        </ul>

        <p class="pt-6 text-sm text-muted-foreground">
          {{
            t('portal.buy.totalPrice', {
              total: `${currencySymbol(currency)}${formatPrice(card.price)}`,
              months: billingMonths(card.durationDays)
            })
          }}
        </p>

        <Button
          class="mt-4 h-11 w-full"
          @click="subscribe(card.plan.id, card.plan.cycles[0].id)"
        >
          {{ t('portal.buy.subscribeNow') }}
        </Button>
      </div>
    </div>
  </div>
</template>
