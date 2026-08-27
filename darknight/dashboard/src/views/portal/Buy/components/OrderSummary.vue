<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { Check } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { previewCoupon } from '@/api/portal/orders'
import { resolvePortalApiError } from '@/utils/portalError'
import { currencySymbol, formatPrice, getCycleLabelKey, getPlanMeta } from '../plans'
import { usePlanCatalog } from '../usePlanCatalog'

const props = defineProps<{
  planId: string
  cycleId: string
  coupon?: string
  submitLabel: string
  loading?: boolean
  /** 订单页传入下单时锁定的金额；不传则取当前价目表 */
  amount?: number
  /** 订单页传入下单时锁定的折扣 */
  discount?: number
  currency?: string
  hideSubmit?: boolean
  readonlyCoupon?: boolean
}>()

const emit = defineEmits<{
  'update:coupon': [value: string]
  submit: []
}>()

const { t } = useI18n()
const { currency: catalogCurrency, getCycle } = usePlanCatalog()
const couponInput = ref(props.coupon ?? '')
const verifying = ref(false)
/** 已通过后端校验的折扣；仅用于展示，最终金额仍由后端下单时计算 */
const verifiedDiscount = ref(0)

const planName = computed(() => getPlanMeta(props.planId)?.name ?? props.planId)
const currencyCode = computed(() => props.currency ?? catalogCurrency.value)
const symbol = computed(() => currencySymbol(currencyCode.value))

const discount = computed(() => props.discount ?? verifiedDiscount.value)

/** 订单页显示下单时锁定的原价，配置页显示当前价目表原价 */
const listPrice = computed(() => {
  if (props.amount !== undefined) {
    return Math.round((props.amount + discount.value) * 100) / 100
  }
  return getCycle(props.planId, props.cycleId)?.price
})

const total = computed(() => {
  if (props.amount !== undefined) return props.amount
  if (listPrice.value === undefined) return undefined
  return Math.round((listPrice.value - discount.value) * 100) / 100
})

const summaryLine = computed(() => `${planName.value} x ${t(getCycleLabelKey(props.cycleId))}`)

// 换套餐或换周期后旧折扣不再适用，重新校验前先清掉。
watch([() => props.planId, () => props.cycleId], () => {
  verifiedDiscount.value = 0
  emit('update:coupon', '')
})

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
      cycle_id: props.cycleId,
      coupon: code
    })
    verifiedDiscount.value = preview.discount
    emit('update:coupon', preview.coupon)
    ElMessage.success(
      t('portal.buy.couponApplied', { amount: symbol.value + formatPrice(preview.discount) })
    )
  } catch (err) {
    verifiedDiscount.value = 0
    emit('update:coupon', '')
    ElMessage.error(resolvePortalApiError(err, t))
  } finally {
    verifying.value = false
  }
}
</script>

<template>
  <aside class="order-summary">
    <div v-if="!readonlyCoupon" class="coupon-box">
      <el-input
        v-model="couponInput"
        :placeholder="t('portal.buy.couponPlaceholder')"
        @keyup.enter="verifyCoupon"
      />
      <el-button
        type="primary"
        class="coupon-btn"
        :loading="verifying"
        @click="verifyCoupon"
      >
        {{ t('portal.buy.verifyCoupon') }}
      </el-button>
    </div>

    <el-card shadow="never" class="summary-card">
      <div class="summary-title">{{ t('portal.buy.orderTotal') }}</div>
      <div class="summary-line">
        <span>{{ summaryLine }}</span>
        <span>{{ listPrice === undefined ? '--' : symbol + formatPrice(listPrice) }}</span>
      </div>
      <div v-if="discount > 0" class="summary-line discount-line">
        <span>{{ coupon || t('portal.buy.verifyCoupon') }}</span>
        <span>-{{ symbol }}{{ formatPrice(discount) }}</span>
      </div>
      <div class="summary-total">
        <span>{{ symbol }}</span>
        <strong>{{ total === undefined ? '--' : formatPrice(total) }}</strong>
        <small>{{ currencyCode }}</small>
      </div>
      <el-button
        v-if="!hideSubmit"
        type="primary"
        class="submit-btn"
        :loading="loading"
        :disabled="total === undefined"
        @click="emit('submit')"
      >
        <el-icon v-if="!loading"><Check /></el-icon>
        {{ submitLabel }}
      </el-button>
    </el-card>
  </aside>
</template>

<style scoped>
.order-summary {
  width: 320px;
  flex-shrink: 0;
}

.coupon-box {
  display: flex;
  padding: 16px;
  margin-bottom: 16px;
  background: #fff;
  border-radius: 8px;
  gap: 8px;
}

.coupon-btn {
  flex-shrink: 0;
  background: #20a397;
  border-color: #20a397;
}

.summary-card {
  padding: 4px;
}

.summary-title {
  margin-bottom: 16px;
  font-size: 16px;
  font-weight: 700;
  color: #303133;
}

.summary-line {
  display: flex;
  margin-bottom: 20px;
  font-size: 14px;
  color: #606266;
  justify-content: space-between;
  gap: 12px;
}

.discount-line {
  margin-top: -12px;
  color: #20a397;
}

.summary-total {
  display: flex;
  margin-bottom: 20px;
  align-items: baseline;
  gap: 4px;
}

.summary-total span {
  font-size: 20px;
  font-weight: 600;
}

.summary-total strong {
  font-size: 36px;
  font-weight: 700;
  line-height: 1;
}

.summary-total small {
  font-size: 14px;
  color: #909399;
}

.submit-btn {
  width: 100%;
  height: 44px;
  background: #20a397;
  border-color: #20a397;
}

@media (width <= 960px) {
  .order-summary {
    width: 100%;
  }
}
</style>
