<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import OrderSummary from '../Buy/components/OrderSummary.vue'
import { closeOrder, formatOrderTime, getOrder, updateOrder } from '../Buy/orders'
import { PAYMENT_METHODS, getCycle, getPlanById, type PaymentMethodId } from '../Buy/plans'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()

const orderId = computed(() => String(route.params.orderId || ''))
const order = computed(() => getOrder(orderId.value))
const plan = computed(() => (order.value ? getPlanById(order.value.planId) : undefined))
const cycle = computed(() =>
  plan.value && order.value ? getCycle(plan.value, order.value.cycleId) : undefined
)

const selectedPayment = ref<PaymentMethodId>('alipay_1')
const checkingOut = ref(false)

watch(
  order,
  (value) => {
    if (value?.paymentMethod) {
      selectedPayment.value = value.paymentMethod
    }
    if (orderId.value && !value) {
      router.replace({ name: 'portal-buy' })
    }
    if (value?.status === 'closed') {
      router.replace({ name: 'portal-buy' })
    }
  },
  { immediate: true }
)

async function onCloseOrder() {
  await ElMessageBox.confirm(t('portal.buy.closeOrderConfirm'), t('portal.buy.closeOrder'), {
    type: 'warning'
  })
  closeOrder(orderId.value)
  ElMessage.success(t('portal.buy.closeOrderSuccess'))
  router.push({ name: 'portal-buy' })
}

function checkout() {
  if (!order.value) return
  checkingOut.value = true
  updateOrder(order.value.id, { paymentMethod: selectedPayment.value })
  ElMessage.info(t('portal.buy.checkoutMock'))
  checkingOut.value = false
}
</script>

<template>
  <div v-if="order && plan && cycle" class="order-page">
    <div class="order-main">
      <el-card shadow="never" class="info-card">
        <div class="info-title">{{ t('portal.buy.productInfo') }}</div>
        <div class="info-row">
          <span>{{ t('portal.buy.productTraffic') }}</span>
          <strong>{{ plan.name }}</strong>
        </div>
      </el-card>

      <el-card shadow="never" class="info-card">
        <div class="info-head">
          <div class="info-title">{{ t('portal.buy.orderInfo') }}</div>
          <el-button size="small" @click="onCloseOrder">{{ t('portal.buy.closeOrder') }}</el-button>
        </div>
        <div class="info-row">
          <span>{{ t('portal.buy.orderNo') }}</span>
          <strong>{{ order.id }}</strong>
        </div>
        <div class="info-row">
          <span>{{ t('portal.buy.createdAt') }}</span>
          <strong>{{ formatOrderTime(order.createdAt) }}</strong>
        </div>
      </el-card>

      <el-card shadow="never" class="info-card">
        <div class="info-title">{{ t('portal.buy.paymentMethod') }}</div>
        <button
          v-for="method in PAYMENT_METHODS"
          :key="method.id"
          type="button"
          class="payment-option"
          :class="{ active: selectedPayment === method.id }"
          @click="selectedPayment = method.id"
        >
          {{ t(method.labelKey) }}
        </button>
      </el-card>
    </div>

    <OrderSummary
      :plan-id="plan.id"
      :cycle-id="order.cycleId"
      :coupon="order.coupon"
      :loading="checkingOut"
      :submit-label="t('portal.buy.checkout')"
      @submit="checkout"
    />
  </div>
</template>

<style scoped>
.order-page {
  display: flex;
  gap: 20px;
  align-items: flex-start;
}

.order-main {
  flex: 1;
  min-width: 0;
}

.info-card {
  margin-bottom: 16px;
}

.info-head {
  display: flex;
  margin-bottom: 16px;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.info-title {
  font-size: 16px;
  font-weight: 700;
  color: #303133;
}

.info-row {
  display: flex;
  padding: 10px 0;
  font-size: 14px;
  color: #606266;
  justify-content: space-between;
  gap: 16px;
}

.payment-option {
  display: block;
  width: 100%;
  padding: 16px 18px;
  margin-bottom: 12px;
  font-size: 15px;
  color: #303133;
  text-align: left;
  cursor: pointer;
  background: #fff;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
}

.payment-option:last-child {
  margin-bottom: 0;
}

.payment-option.active {
  border-color: #20a397;
  box-shadow: 0 0 0 1px #20a397 inset;
}

@media (width <= 960px) {
  .order-page {
    flex-direction: column;
  }
}
</style>
