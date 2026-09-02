<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { Check } from 'lucide-vue-next'
import { toast } from 'vue-sonner'
import { previewCoupon } from '@/api/portal/orders'
import { resolvePortalApiError } from '@/utils/portalError'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Separator } from '@/components/ui/separator'
import { cn } from '@/lib/utils'
import { currencySymbol, formatPrice } from '../plans'
import { usePlanCatalog } from '../usePlanCatalog'

const props = withDefaults(
  defineProps<{
    planId: string
    coupon?: string
    submitLabel: string
    loading?: boolean
    /** 订单页传入下单时锁定的金额；不传则取当前价目表 */
    amount?: number
    /** 订单页传入下单时锁定的折扣 */
    discount?: number
    /** 订单页传入下单时锁定的佣金抵扣 */
    walletCredit?: number
    /** 套餐原价；订单页优先用价目表原价，避免明细缺失 */
    listPriceOverride?: number
    /** 配置页预览：当前可用佣金余额 */
    availableCommission?: number
    currency?: string
    hideSubmit?: boolean
    readonlyCoupon?: boolean
    /** panel：结算页左栏，无外框；aside：配置页右侧卡片 */
    variant?: 'panel' | 'aside'
  }>(),
  { variant: 'aside' }
)

const emit = defineEmits<{
  'update:coupon': [value: string]
  submit: []
}>()

const { t } = useI18n()
const { currency: catalogCurrency, getPlan } = usePlanCatalog()
const couponInput = ref(props.coupon ?? '')
const verifying = ref(false)
/** 已通过后端校验的折扣；仅用于展示，最终金额仍由后端下单时计算 */
const verifiedDiscount = ref(0)

const plan = computed(() => getPlan(props.planId))
const planName = computed(() => plan.value?.name ?? props.planId)
const currencyCode = computed(() => props.currency ?? catalogCurrency.value)
const symbol = computed(() => currencySymbol(currencyCode.value))

const discount = computed(() => props.discount ?? verifiedDiscount.value)
const walletCredit = computed(() => props.walletCredit ?? 0)
const isPreview = computed(() => props.availableCommission !== undefined && props.amount === undefined)

/** 套餐原价 */
const listPrice = computed(() => {
  if (props.listPriceOverride !== undefined) return props.listPriceOverride
  if (props.amount !== undefined) {
    return Math.round((props.amount + discount.value + walletCredit.value) * 100) / 100
  }
  return plan.value?.price
})

/** 实际或预计佣金抵扣 */
const commissionCredit = computed(() => {
  if (walletCredit.value > 0) return walletCredit.value
  if (props.amount !== undefined && listPrice.value !== undefined) {
    const implied = Math.round((listPrice.value - discount.value - props.amount) * 100) / 100
    return implied > 0 ? implied : 0
  }
  if (isPreview.value && listPrice.value !== undefined) {
    const payable = Math.round((listPrice.value - discount.value) * 100) / 100
    return Math.round(Math.min(props.availableCommission ?? 0, payable) * 100) / 100
  }
  return 0
})

const total = computed(() => {
  if (props.amount !== undefined) return props.amount
  if (listPrice.value === undefined) return undefined
  return Math.round((listPrice.value - discount.value - commissionCredit.value) * 100) / 100
})

const durationDays = computed(() => plan.value?.durationDays ?? 0)
const planDescription = computed(() =>
  durationDays.value > 0
    ? t('portal.buy.planDescription', { plan: planName.value, days: durationDays.value })
    : ''
)

watch(
  () => props.planId,
  () => {
    verifiedDiscount.value = 0
    emit('update:coupon', '')
  }
)

async function verifyCoupon() {
  const code = couponInput.value.trim()
  if (!code) {
    verifiedDiscount.value = 0
    emit('update:coupon', '')
    return
  }

  verifying.value = true
  try {
    const preview = await previewCoupon({
      plan_id: props.planId,
      coupon: code
    })
    verifiedDiscount.value = preview.discount
    emit('update:coupon', preview.coupon)
    toast.success(
      t('portal.buy.couponApplied', { amount: symbol.value + formatPrice(preview.discount) })
    )
  } catch (err) {
    verifiedDiscount.value = 0
    emit('update:coupon', '')
    toast.error(resolvePortalApiError(err, t))
  } finally {
    verifying.value = false
  }
}
</script>

<template>
  <aside
    :class="
      cn(
        'flex flex-col gap-6',
        variant === 'aside'
          ? 'w-full shrink-0 rounded-xl border border-border bg-card p-6 lg:w-80'
          : 'h-full bg-muted/40 p-8'
      )
    "
  >
    <div class="space-y-4">
      <p class="text-sm font-medium text-muted-foreground">{{ t('portal.buy.orderOverview') }}</p>
      <p class="text-4xl font-bold tracking-tight text-primary">
        {{ total === undefined ? '--' : symbol + formatPrice(total) }}
      </p>
      <div class="space-y-1">
        <p class="text-base font-semibold text-foreground">{{ planName }}</p>
        <p v-if="planDescription" class="text-sm leading-relaxed text-muted-foreground">
          {{ planDescription }}
        </p>
      </div>
    </div>

    <Separator />

    <div class="space-y-3 text-sm">
      <div class="flex items-center justify-between">
        <span class="text-muted-foreground">{{ t('portal.buy.subtotal') }}</span>
        <span class="font-medium text-foreground">
          {{ listPrice === undefined ? '--' : symbol + formatPrice(listPrice) }}
        </span>
      </div>

      <div v-if="!readonlyCoupon" class="flex items-center gap-2">
        <Input
          v-model="couponInput"
          :placeholder="t('portal.buy.couponPlaceholder')"
          class="h-9"
          @keyup.enter="verifyCoupon"
        />
        <Button variant="outline" size="sm" :disabled="verifying" @click="verifyCoupon">
          {{ t('portal.buy.verifyCoupon') }}
        </Button>
      </div>

      <div v-if="discount > 0" class="flex items-center justify-between">
        <span class="text-muted-foreground">{{ coupon || t('portal.buy.discount') }}</span>
        <span class="font-medium text-primary">-{{ symbol }}{{ formatPrice(discount) }}</span>
      </div>

      <div v-if="commissionCredit > 0" class="flex items-center justify-between">
        <span class="text-muted-foreground">
          {{
            isPreview
              ? t('portal.buy.commissionCreditPreview')
              : t('portal.buy.commissionCredit')
          }}
        </span>
        <span class="font-medium text-primary">-{{ symbol }}{{ formatPrice(commissionCredit) }}</span>
      </div>
    </div>

    <Separator />

    <div class="flex items-baseline justify-between">
      <span class="text-sm font-medium text-muted-foreground">{{
        t('portal.buy.grandTotal')
      }}</span>
      <span class="text-xl font-bold text-foreground">
        {{ total === undefined ? '--' : symbol + formatPrice(total) }}
        <span class="ms-1 text-xs font-normal text-muted-foreground">{{ currencyCode }}</span>
      </span>
    </div>

    <Button
      v-if="!hideSubmit"
      class="mt-auto h-11 w-full"
      :disabled="loading || total === undefined"
      @click="emit('submit')"
    >
      <Check v-if="!loading" class="me-2 size-4" />
      {{ submitLabel }}
    </Button>
  </aside>
</template>
