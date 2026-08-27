<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { loadScript, type PayPalCardFieldsComponent } from '@paypal/paypal-js'
import { capturePortalOrder, fetchPayPalConfig, type PortalOrder } from '@/api/portal/orders'
import { resolvePortalApiError } from '@/utils/portalError'
import { currencySymbol, formatPrice } from '../plans'

const props = defineProps<{
  orderId: string
  paypalOrderId: string
  amount: number
  currency: string
}>()

const emit = defineEmits<{
  success: [order: PortalOrder]
  error: [message: string]
}>()

const { t } = useI18n()
const loading = ref(true)
const paying = ref(false)
const ready = ref(false)
const cardFields = ref<PayPalCardFieldsComponent | null>(null)

let destroyed = false
/**
 * 扣款成功后 PayPal SDK 仍可能回调 onError 或让 submit() reject（订单已不可再支付），
 * 此时不能再向用户报错。同一次尝试内也只提示一次，避免多条通道重复弹窗。
 */
let settled = false
let errorNotified = false

function reportError(message: string) {
  if (settled || destroyed || errorNotified) return
  errorNotified = true
  emit('error', message)
}

async function initCardFields() {
  loading.value = true
  ready.value = false
  errorNotified = false

  try {
    const config = await fetchPayPalConfig()
    if (!config.enabled || !config.client_id) {
      reportError(t('portal.buy.paypalNotConfigured'))
      return
    }

    const paypal = await loadScript({
      clientId: config.client_id,
      components: 'card-fields',
      currency: config.currency
    })

    if (!paypal?.CardFields || destroyed) return

    const fields = paypal.CardFields({
      createOrder: () => Promise.resolve(props.paypalOrderId),
      onApprove: async () => {
        paying.value = true
        try {
          const { order } = await capturePortalOrder(props.orderId)
          // 保持按钮 loading 直到父组件切走表单，避免重复提交。
          settled = true
          emit('success', order)
        } catch (err) {
          paying.value = false
          reportError(resolvePortalApiError(err, t))
        }
      },
      onError: () => {
        if (settled) return
        paying.value = false
        reportError(t('portal.buy.paymentFailed'))
      }
    })

    if (!fields.isEligible()) {
      reportError(t('portal.buy.cardNotEligible'))
      return
    }

    cardFields.value = fields
    await Promise.all([
      fields.NameField({}).render('#paypal-card-name'),
      fields.NumberField({}).render('#paypal-card-number'),
      fields.ExpiryField({}).render('#paypal-card-expiry'),
      fields.CVVField({}).render('#paypal-card-cvv')
    ])

    if (!destroyed) {
      ready.value = true
    }
  } catch {
    reportError(t('portal.buy.paypalLoadFailed'))
  } finally {
    if (!destroyed) {
      loading.value = false
    }
  }
}

async function submitPayment() {
  if (!cardFields.value || paying.value || settled) return
  paying.value = true
  errorNotified = false
  try {
    await cardFields.value.submit()
  } catch {
    if (settled) return
    paying.value = false
    reportError(t('portal.buy.paymentFailed'))
  }
}

watch(
  () => props.paypalOrderId,
  () => {
    if (props.paypalOrderId) {
      initCardFields()
    }
  }
)

onMounted(() => {
  if (props.paypalOrderId) {
    initCardFields()
  }
})

onBeforeUnmount(() => {
  destroyed = true
})

defineExpose({ submitPayment })
</script>

<template>
  <div v-loading="loading" class="paypal-card-form">
    <div class="field-group">
      <label>{{ t('portal.buy.cardNumber') }}</label>
      <div id="paypal-card-number" class="paypal-field" />
    </div>
    <div class="field-group">
      <label>{{ t('portal.buy.cardName') }}</label>
      <div id="paypal-card-name" class="paypal-field" />
    </div>
    <div class="field-row">
      <div class="field-group">
        <label>{{ t('portal.buy.cardExpiry') }}</label>
        <div id="paypal-card-expiry" class="paypal-field" />
      </div>
      <div class="field-group">
        <label>{{ t('portal.buy.cardCvv') }}</label>
        <div id="paypal-card-cvv" class="paypal-field" />
      </div>
    </div>
    <el-button
      type="primary"
      class="pay-btn"
      :disabled="!ready || paying"
      :loading="paying"
      @click="submitPayment"
    >
      {{ t('portal.buy.payAmount', { amount: currencySymbol(currency) + formatPrice(amount) }) }}
    </el-button>
    <p class="powered-by">{{ t('portal.buy.poweredByPayPal') }}</p>
  </div>
</template>

<style scoped>
.paypal-card-form {
  min-height: 220px;
}

.field-group {
  margin-bottom: 16px;
}

.field-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  color: #606266;
}

.field-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.paypal-field {
  min-height: 44px;
  padding: 4px 12px;
  background: #fff;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
}

.pay-btn {
  width: 100%;
  height: 44px;
  margin-top: 8px;
  background: #20a397;
  border-color: #20a397;
}

.powered-by {
  margin: 12px 0 0;
  font-size: 12px;
  color: #909399;
  text-align: center;
}
</style>
