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
import PlanDiscountBurst from './PlanDiscountBurst.vue'
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
  <div class="w-full">
    <h2 class="mb-5 text-2xl font-bold tracking-tight text-foreground">
      {{ t('portal.buy.choosePlan') }}
    </h2>

    <Alert v-if="isError" variant="destructive" class="mb-4">
      <AlertDescription>{{ t('portal.buy.plansLoadFailed') }}</AlertDescription>
    </Alert>

    <div
      v-if="isLoading"
      class="grid justify-start gap-4 grid-cols-[repeat(auto-fill,270px)]"
    >
      <Skeleton v-for="i in 4" :key="i" class="h-[26rem] rounded-xl" />
    </div>

    <div
      v-else
      class="grid justify-start items-stretch gap-4 grid-cols-[repeat(auto-fill,270px)]"
    >
      <div
        v-for="card in planCards"
        :key="card.plan.id"
        :class="
          cn(
            'relative flex flex-col rounded-xl border bg-card p-5 transition-shadow hover:shadow-lg',
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

        <div class="relative min-h-[4.25rem]">
          <p class="pe-[4.5rem] text-xl font-bold leading-tight text-foreground">
            {{ card.plan.name }}
          </p>

          <div class="absolute end-0 top-4">
            <PlanDiscountBurst
              :percent="card.discount"
              :label="
                card.discount > 0
                  ? t('portal.buy.discountShort')
                  : t('portal.buy.noDiscount')
              "
            />
          </div>
        </div>

        <div class="mt-1 flex items-baseline gap-1">
          <span class="text-base font-semibold text-foreground">{{ currencySymbol(currency) }}</span>
          <span class="text-3xl font-bold leading-none tracking-tight text-foreground">
            {{ formatPrice(card.monthlyPrice) }}
          </span>
          <span class="text-sm text-muted-foreground">{{ t('portal.buy.perMonth') }}</span>
        </div>

        <ul v-if="card.plan.features.length" class="mt-4 flex-1 space-y-1.5">
          <li
            v-for="(feature, index) in card.plan.features"
            :key="index"
            class="flex items-start gap-2 text-xs leading-relaxed text-muted-foreground"
          >
            <Check class="mt-0.5 size-4 shrink-0 text-primary" />
            <span>{{ feature }}</span>
          </li>
        </ul>

        <p class="pt-4 text-xs text-muted-foreground">
          {{
            t('portal.buy.totalPrice', {
              total: `${currencySymbol(currency)}${formatPrice(card.price)}`,
              months: billingMonths(card.durationDays)
            })
          }}
        </p>

        <Button
          class="mt-3 h-10 w-full text-sm"
          @click="subscribe(card.plan.id, card.plan.cycles[0].id)"
        >
          {{ t('portal.buy.subscribeNow') }}
        </Button>
      </div>
    </div>
  </div>
</template>
