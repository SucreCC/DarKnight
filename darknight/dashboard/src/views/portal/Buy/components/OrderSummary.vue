<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Check } from '@element-plus/icons-vue'
import type { BillingCycleId } from '../plans'
import { formatPrice, getCycle, getPlanById } from '../plans'

const props = defineProps<{
  planId: string
  cycleId: BillingCycleId
  coupon?: string
  submitLabel: string
  loading?: boolean
}>()

const emit = defineEmits<{
  'update:cycleId': [value: BillingCycleId]
  'update:coupon': [value: string]
  submit: []
}>()

const { t } = useI18n()
const couponInput = ref(props.coupon ?? '')

const plan = computed(() => getPlanById(props.planId))
const selectedCycle = computed(() =>
  plan.value ? getCycle(plan.value, props.cycleId) : undefined
)

const summaryLine = computed(() => {
  if (!plan.value || !selectedCycle.value) return ''
  return `${plan.value.name} x ${t(selectedCycle.value.labelKey)}`
})

function selectCycle(id: BillingCycleId) {
  emit('update:cycleId', id)
}

function verifyCoupon() {
  emit('update:coupon', couponInput.value.trim())
}
</script>

<template>
  <aside v-if="plan && selectedCycle" class="order-summary">
    <div class="coupon-box">
      <el-input
        v-model="couponInput"
        :placeholder="t('portal.buy.couponPlaceholder')"
        @keyup.enter="verifyCoupon"
      />
      <el-button type="primary" class="coupon-btn" @click="verifyCoupon">
        {{ t('portal.buy.verifyCoupon') }}
      </el-button>
    </div>

    <el-card shadow="never" class="summary-card">
      <div class="summary-title">{{ t('portal.buy.orderTotal') }}</div>
      <div class="summary-line">
        <span>{{ summaryLine }}</span>
        <span>¥{{ formatPrice(selectedCycle.price) }}</span>
      </div>
      <div class="summary-total">
        <span>¥</span>
        <strong>{{ formatPrice(selectedCycle.price) }}</strong>
        <small>CNY</small>
      </div>
      <el-button
        type="primary"
        class="submit-btn"
        :loading="loading"
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
