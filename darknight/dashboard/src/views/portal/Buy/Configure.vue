<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { Check, Loader2 } from 'lucide-vue-next'
import { toast } from 'vue-sonner'
import { createPortalOrder, preparePortalOrderPayment } from '@/api/portal/orders'
import { finishCheckoutBoot, startCheckoutBoot } from './checkoutBoot'
import { preloadPayPalSdk } from './paypalPreload'
import { resolvePortalApiError } from '@/utils/portalError'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { cn } from '@/lib/utils'
import OrderSummary from './components/OrderSummary.vue'
import { currencySymbol, formatPrice } from './plans'
import { usePlanCatalog } from './usePlanCatalog'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()

const { currency, getPlan, isLoading, isError } = usePlanCatalog()

const planId = computed(() => String(route.params.planId || ''))
const plan = computed(() => getPlan(planId.value))
const selectedCycleId = ref('')
const coupon = ref('')
const submitting = ref(false)

watch(
  plan,
  (value) => {
    if (value?.cycles[0]) {
      selectedCycleId.value = value.cycles[0].id
    }
  },
  { immediate: true }
)

watch([planId, isLoading], () => {
  if (!isLoading.value && !plan.value) {
    router.replace({ name: 'portal-buy' })
  }
})

preloadPayPalSdk()

async function placeOrder() {
  if (!plan.value) return
  submitting.value = true
  startCheckoutBoot()
  try {
    const order = await createPortalOrder({
      plan_id: plan.value.id,
      cycle_id: selectedCycleId.value,
      coupon: coupon.value.trim() || undefined
    })
    await preparePortalOrderPayment(order.id)
    await router.push({ name: 'portal-order-detail', params: { orderId: order.id } })
  } catch (err) {
    submitting.value = false
    finishCheckoutBoot()
    toast.error(resolvePortalApiError(err, t))
  }
}
</script>

<template>
  <Teleport to="body">
    <div
      v-if="submitting"
      class="fixed inset-0 z-[100] flex flex-col items-center justify-center gap-3 bg-muted"
    >
      <Loader2 class="size-8 animate-spin text-primary" />
      <p class="text-sm text-muted-foreground">{{ t('portal.buy.paymentLoading') }}</p>
    </div>
  </Teleport>

  <Alert v-if="isError" variant="destructive">
    <AlertDescription>{{ t('portal.buy.plansLoadFailed') }}</AlertDescription>
  </Alert>
  <div v-else-if="plan" class="flex flex-col items-start gap-5 lg:flex-row">
    <div class="min-w-0 flex-1 space-y-4">
      <div class="rounded-xl border border-border bg-card p-7">
        <p class="mb-4 text-2xl font-bold text-foreground">{{ plan.name }}</p>
        <ul class="space-y-2.5">
          <li
            v-for="(feature, index) in plan.features"
            :key="index"
            class="flex items-start gap-2 text-sm leading-relaxed text-muted-foreground"
          >
            <Check class="mt-0.5 size-4 shrink-0 text-primary" />
            <span>{{ feature }}</span>
          </li>
        </ul>
      </div>

      <div class="rounded-xl border border-border bg-card p-7">
        <p class="mb-4 text-base font-semibold text-foreground">
          {{ t('portal.buy.paymentCycle') }}
        </p>
        <div class="space-y-3">
          <button
            v-for="cycle in plan.cycles"
            :key="cycle.id"
            type="button"
            :class="
              cn(
                'flex w-full items-center justify-between rounded-lg border px-5 py-4 text-[15px] transition-colors',
                selectedCycleId === cycle.id
                  ? 'border-primary bg-primary/5 text-foreground ring-1 ring-primary'
                  : 'border-border text-foreground hover:border-primary/40'
              )
            "
            @click="selectedCycleId = cycle.id"
          >
            <span>{{ cycle.label }}</span>
            <span class="font-semibold">
              {{ currencySymbol(currency) }}{{ formatPrice(cycle.price) }}
            </span>
          </button>
        </div>
      </div>
    </div>

    <OrderSummary
      :plan-id="plan.id"
      :cycle-id="selectedCycleId"
      :coupon="coupon"
      :loading="submitting"
      :submit-label="t('portal.buy.placeOrder')"
      @update:coupon="coupon = $event"
      @submit="placeOrder"
    />
  </div>
</template>
