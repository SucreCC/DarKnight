<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
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
import { getCycleLabelKey, getPlanMeta } from '../Buy/plans'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()

const orderId = computed(() => String(route.params.orderId || ''))
const order = ref<PortalOrder | null>(null)
const loading = ref(true)
const preparingPayment = ref(false)
const paymentError = ref('')

const planName = computed(() =>
  order.value ? (getPlanMeta(order.value.plan_id)?.name ?? order.value.plan_id) : ''
)
const cycleLabel = computed(() =>
  order.value ? t(getCycleLabelKey(order.value.cycle_id)) : ''
)
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
    ElMessage.error(resolvePortalApiError(err, t))
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
  } finally {
    preparingPayment.value = false
  }
}

watch(orderId, loadOrder, { immediate: true })

async function onCloseOrder() {
  try {
    await ElMessageBox.confirm(t('portal.buy.closeOrderConfirm'), t('portal.buy.closeOrder'), {
      type: 'warning'
    })
  } catch {
    return
  }

  try {
    await closePortalOrder(orderId.value)
    ElMessage.success(t('portal.buy.closeOrderSuccess'))
    router.push({ name: 'portal-orders' })
  } catch (err) {
    ElMessage.error(resolvePortalApiError(err, t))
  }
}

function onPaymentSuccess(paid: PortalOrder) {
  order.value = paid
  paymentError.value = ''
  ElMessage.success(t('portal.buy.paymentSuccess'))
}

async function onPaymentError(message: string) {
  ElMessage.error(message)

  // 失败的那次尝试已经把 PayPal 订单用掉了，必须换一个新的，
  // 否则下一次提交是对着作废订单打，永远失败。
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
  <div v-loading="loading" class="order-wrapper">
    <div v-if="order" class="order-page">
      <div class="order-main">
        <div v-if="isPaid" class="success-card">
          <el-result
            icon="success"
            :title="t('portal.buy.paymentSuccess')"
            :sub-title="t('portal.buy.paymentSuccessHint', { plan: planName, cycle: cycleLabel })"
          >
            <template #extra>
              <el-button type="primary" @click="router.push({ name: 'portal-dashboard' })">
                {{ t('portal.buy.goDashboard') }}
              </el-button>
              <el-button @click="router.push({ name: 'portal-docs' })">
                {{ t('portal.buy.goDocs') }}
              </el-button>
            </template>
          </el-result>
        </div>

        <el-card shadow="never" class="info-card">
          <div class="info-title">{{ t('portal.buy.productInfo') }}</div>
          <div class="info-row">
            <span>{{ t('portal.buy.productTraffic') }}</span>
            <strong>{{ planName }}</strong>
          </div>
          <div class="info-row">
            <span>{{ t('portal.buy.paymentCycle') }}</span>
            <strong>{{ cycleLabel }}</strong>
          </div>
        </el-card>

        <el-card shadow="never" class="info-card">
          <div class="info-head">
            <div class="info-title">{{ t('portal.buy.orderInfo') }}</div>
            <el-button v-if="order.status === 'pending'" size="small" @click="onCloseOrder">
              {{ t('portal.buy.closeOrder') }}
            </el-button>
          </div>
          <div class="info-row">
            <span>{{ t('portal.buy.orderNo') }}</span>
            <strong>{{ order.id }}</strong>
          </div>
          <div class="info-row">
            <span>{{ t('portal.buy.createdAt') }}</span>
            <strong>{{ formatOrderTime(order.created_at) }}</strong>
          </div>
          <div v-if="order.paid_at" class="info-row">
            <span>{{ t('portal.buy.paidAt') }}</span>
            <strong>{{ formatOrderTime(order.paid_at) }}</strong>
          </div>
        </el-card>

        <el-card
          v-if="order.status === 'pending'"
          v-loading="preparingPayment"
          shadow="never"
          class="info-card"
        >
          <div class="info-title">{{ t('portal.buy.paymentMethod') }}</div>
          <PayPalCardForm
            v-if="order.paypal_order_id"
            :order-id="order.id"
            :paypal-order-id="order.paypal_order_id"
            :amount="order.amount"
            :currency="order.currency"
            @success="onPaymentSuccess"
            @error="onPaymentError"
          />
          <div v-else-if="paymentError" class="payment-error">
            <el-alert type="error" :title="paymentError" show-icon :closable="false" />
            <el-button class="retry-btn" @click="ensurePaymentReady(true)">
              {{ t('portal.buy.retryPayment') }}
            </el-button>
          </div>
        </el-card>

        <el-alert
          v-else-if="order.status === 'failed'"
          type="error"
          :title="t('portal.buy.paymentFailed')"
          show-icon
          :closable="false"
        />
      </div>

      <OrderSummary
        :plan-id="order.plan_id"
        :cycle-id="order.cycle_id"
        :coupon="order.coupon || undefined"
        :amount="order.amount"
        :discount="order.discount"
        :currency="order.currency"
        :submit-label="t('portal.buy.checkout')"
        hide-submit
        readonly-coupon
      />
    </div>
  </div>
</template>

<style scoped>
.order-wrapper {
  min-height: 200px;
}

.order-page {
  display: flex;
  gap: 20px;
  align-items: flex-start;
}

.order-main {
  flex: 1;
  min-width: 0;
}

.success-card {
  margin-bottom: 16px;
  background: #fff;
  border-radius: 8px;
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
  margin-bottom: 16px;
  font-size: 16px;
  font-weight: 700;
  color: #303133;
}

.info-head .info-title {
  margin-bottom: 0;
}

.info-row {
  display: flex;
  padding: 10px 0;
  font-size: 14px;
  color: #606266;
  justify-content: space-between;
  gap: 16px;
}

.payment-error {
  display: flex;
  flex-direction: column;
  gap: 12px;
  align-items: flex-start;
}

@media (width <= 960px) {
  .order-page {
    flex-direction: column;
  }
}
</style>
