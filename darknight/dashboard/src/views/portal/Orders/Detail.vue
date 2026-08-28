<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { CircleCheckBig, X } from 'lucide-vue-next'
import { toast } from 'vue-sonner'
import OrderSummary from '../Buy/components/OrderSummary.vue'
import PayPalCardForm from '../Buy/components/PayPalCardForm.vue'
import {
  closePortalOrder,
  fetchPortalOrder,
  formatOrderTime,
  preparePortalOrderPayment,
  type PortalOrder
} from '@/api/portal/orders'
import { resolvePortalApiError } from '@/utils/portalError'
import { useConfirm } from '@/composables/useConfirm'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
import LoadingOverlay from '@/components/LoadingOverlay/index.vue'
import { getCycleLabelKey, getPlanMeta } from '../Buy/plans'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const { confirm } = useConfirm()

const orderId = computed(() => String(route.params.orderId || ''))
const order = ref<PortalOrder | null>(null)
const loading = ref(true)
const preparingPayment = ref(false)
const paymentError = ref('')

const planName = computed(() =>
  order.value ? (getPlanMeta(order.value.plan_id)?.name ?? order.value.plan_id) : ''
)
const cycleLabel = computed(() => (order.value ? t(getCycleLabelKey(order.value.cycle_id)) : ''))
const isPaid = computed(() => order.value?.status === 'paid')

async function loadOrder() {
  loading.value = true
  paymentError.value = ''
  try {
    order.value = await fetchPortalOrder(orderId.value)
    if (order.value.status === 'closed') {
      router.replace({ name: 'portal-orders' })
      return
    }
    if (order.value.status === 'pending' && !order.value.paypal_order_id) {
      await ensurePaymentReady()
    }
  } catch (err) {
    toast.error(resolvePortalApiError(err, t))
    router.replace({ name: 'portal-orders' })
  } finally {
    loading.value = false
  }
}

async function ensurePaymentReady(refresh = false) {
  preparingPayment.value = true
  paymentError.value = ''
  try {
    order.value = await preparePortalOrderPayment(orderId.value, { refresh })
  } catch (err) {
    paymentError.value = resolvePortalApiError(err, t)
    if (order.value) {
      order.value.paypal_order_id = null
    }
  } finally {
    preparingPayment.value = false
  }
}

watch(orderId, loadOrder, { immediate: true })

async function onCloseOrder() {
  try {
    await confirm({
      title: t('portal.buy.closeOrder'),
      description: t('portal.buy.closeOrderConfirm'),
      destructive: true
    })
  } catch {
    return
  }

  try {
    await closePortalOrder(orderId.value)
    toast.success(t('portal.buy.closeOrderSuccess'))
    router.push({ name: 'portal-orders' })
  } catch (err) {
    toast.error(resolvePortalApiError(err, t))
  }
}

function onPaymentSuccess(paid: PortalOrder) {
  order.value = paid
  paymentError.value = ''
  toast.success(t('portal.buy.paymentSuccess'))
}

async function onPaymentError(_message: string, refreshOrder = true) {
  if (!refreshOrder) return

  try {
    order.value = await fetchPortalOrder(orderId.value)
  } catch {
    return
  }
  if (order.value.status === 'pending') {
    await ensurePaymentReady(true)
  }
}
</script>

<template>
  <div class="min-h-screen bg-muted px-4 py-10">
    <LoadingOverlay
      :loading="loading && !order"
      class="mx-auto w-full max-w-5xl"
      :class="{ 'min-h-[60vh]': loading && !order }"
    >
      <div
        v-if="order"
        class="overflow-hidden rounded-2xl border border-border bg-card shadow-xl min-[960px]:grid min-[960px]:grid-cols-[minmax(0,380px)_minmax(0,1fr)]"
      >
        <OrderSummary
          :plan-id="order.plan_id"
          :cycle-id="order.cycle_id"
          :coupon="order.coupon || undefined"
          :amount="order.amount"
          :discount="order.discount"
          :currency="order.currency"
          :submit-label="t('portal.buy.checkout')"
          variant="panel"
          hide-submit
          readonly-coupon
        />

        <div class="p-8">
          <div
            v-if="isPaid"
            class="flex h-full flex-col items-center justify-center gap-4 text-center"
          >
            <CircleCheckBig class="size-14 text-primary" />
            <h2 class="text-xl font-semibold text-foreground">{{
              t('portal.buy.paymentSuccess')
            }}</h2>
            <p class="max-w-sm text-sm text-muted-foreground">
              {{ t('portal.buy.paymentSuccessHint', { plan: planName, cycle: cycleLabel }) }}
            </p>
            <div class="mt-2 flex flex-wrap items-center justify-center gap-3">
              <Button @click="router.push({ name: 'portal-dashboard' })">
                {{ t('portal.buy.goDashboard') }}
              </Button>
              <Button variant="outline" @click="router.push({ name: 'portal-docs' })">
                {{ t('portal.buy.goDocs') }}
              </Button>
            </div>
          </div>

          <template v-else>
            <div class="mb-8 flex items-center gap-2 text-sm">
              <span class="text-muted-foreground">{{ t('portal.buy.stepOrder') }}</span>
              <span class="text-muted-foreground">&rsaquo;</span>
              <span class="font-semibold text-primary">{{ t('portal.buy.stepPayment') }}</span>
              <Button
                v-if="order.status === 'pending'"
                variant="ghost"
                size="icon"
                class="ms-auto text-muted-foreground"
                :aria-label="t('portal.buy.closeOrder')"
                @click="onCloseOrder"
              >
                <X class="size-4" />
              </Button>
            </div>

            <LoadingOverlay
              v-if="order.status === 'pending'"
              :loading="preparingPayment && !order.paypal_order_id"
            >
              <PayPalCardForm
                v-if="order.paypal_order_id"
                :order-id="order.id"
                :paypal-order-id="order.paypal_order_id"
                :amount="order.amount"
                :currency="order.currency"
                @success="onPaymentSuccess"
                @error="onPaymentError"
              />
              <div v-else-if="paymentError" class="space-y-3">
                <Alert variant="destructive">
                  <AlertDescription>{{ paymentError }}</AlertDescription>
                </Alert>
                <Button variant="outline" @click="ensurePaymentReady(true)">
                  {{ t('portal.buy.retryPayment') }}
                </Button>
              </div>
            </LoadingOverlay>

            <Alert v-else-if="order.status === 'failed'" variant="destructive">
              <AlertDescription>{{ t('portal.buy.paymentFailed') }}</AlertDescription>
            </Alert>

            <div class="mt-8 border-t border-border pt-4 text-xs text-muted-foreground">
              {{ t('portal.buy.orderNo') }} {{ order.id }} ·
              {{ formatOrderTime(order.created_at) }}
              <template v-if="order.paid_at">
                · {{ t('portal.buy.paidAt') }} {{ formatOrderTime(order.paid_at) }}
              </template>
            </div>
          </template>
        </div>
      </div>
    </LoadingOverlay>
  </div>
</template>
