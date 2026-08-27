<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { Check } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { createPortalOrder } from '@/api/portal/orders'
import { resolvePortalApiError } from '@/utils/portalError'
import OrderSummary from './components/OrderSummary.vue'
import { currencySymbol, formatPrice, type BillingCycleId } from './plans'
import { usePlanCatalog } from './usePlanCatalog'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()

const { currency, getPlan, isLoading, isError } = usePlanCatalog()

const planId = computed(() => String(route.params.planId || ''))
const plan = computed(() => getPlan(planId.value))
const selectedCycleId = ref<BillingCycleId>('yearly')
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

async function placeOrder() {
  if (!plan.value) return
  submitting.value = true
  try {
    const order = await createPortalOrder({
      plan_id: plan.value.id,
      cycle_id: selectedCycleId.value,
      coupon: coupon.value.trim() || undefined
    })
    router.push({ name: 'portal-order-detail', params: { orderId: order.id } })
  } catch (err) {
    ElMessage.error(resolvePortalApiError(err, t))
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <el-alert
    v-if="isError"
    type="error"
    :title="t('portal.buy.plansLoadFailed')"
    show-icon
    :closable="false"
  />
  <div v-else-if="plan" class="configure-page">
    <div class="configure-main">
      <el-card shadow="never" class="plan-detail-card">
        <div class="plan-detail-name">{{ plan.name }}</div>
        <ul class="plan-detail-features">
          <li v-for="key in plan.featureKeys" :key="key">
            <el-icon class="check-icon"><Check /></el-icon>
            <span>{{ t(key) }}</span>
          </li>
        </ul>
      </el-card>

      <el-card shadow="never" class="cycle-card">
        <div class="section-title">{{ t('portal.buy.paymentCycle') }}</div>
        <button
          v-for="cycle in plan.cycles"
          :key="cycle.id"
          type="button"
          class="cycle-option"
          :class="{ active: selectedCycleId === cycle.id }"
          @click="selectedCycleId = cycle.id"
        >
          <span>{{ t(cycle.labelKey) }}</span>
          <span>{{ currencySymbol(currency) }}{{ formatPrice(cycle.price) }}</span>
        </button>
      </el-card>
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

<style scoped>
.configure-page {
  display: flex;
  gap: 20px;
  align-items: flex-start;
}

.configure-main {
  flex: 1;
  min-width: 0;
}

.plan-detail-card,
.cycle-card {
  margin-bottom: 16px;
}

.plan-detail-name {
  margin-bottom: 16px;
  font-size: 28px;
  font-weight: 700;
}

.plan-detail-features {
  padding: 0;
  margin: 0;
  list-style: none;
}

.plan-detail-features li {
  display: flex;
  padding: 8px 0;
  font-size: 14px;
  line-height: 1.5;
  color: #606266;
  align-items: flex-start;
  gap: 8px;
}

.check-icon {
  margin-top: 3px;
  color: #20a397;
  flex-shrink: 0;
}

.section-title {
  margin-bottom: 16px;
  font-size: 16px;
  font-weight: 700;
}

.cycle-option {
  display: flex;
  width: 100%;
  padding: 16px 18px;
  margin-bottom: 12px;
  font-size: 15px;
  color: #303133;
  cursor: pointer;
  background: #fff;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  justify-content: space-between;
  align-items: center;
}

.cycle-option:last-child {
  margin-bottom: 0;
}

.cycle-option.active {
  border-color: #20a397;
  box-shadow: 0 0 0 1px #20a397 inset;
}

@media (width <= 960px) {
  .configure-page {
    flex-direction: column;
  }
}
</style>
