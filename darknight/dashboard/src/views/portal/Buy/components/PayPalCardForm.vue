<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { loadScript, type PayPalCardFieldsComponent } from '@paypal/paypal-js'
import { capturePortalOrder, fetchPayPalConfig, type PortalOrder } from '@/api/portal/orders'
import { resolvePayPalSdkError, resolvePortalApiError } from '@/utils/portalError'
import { useThemeStore } from '@/store/modules/theme'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import LoadingOverlay from '@/components/LoadingOverlay/index.vue'
import { currencySymbol, formatPrice } from '../plans'
import { readPayPalFieldStyle } from './paypalFieldStyle'

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
const theme = useThemeStore()
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
let renderedFields: { close: () => void }[] = []

function reportError(message: string) {
  if (settled || destroyed || errorNotified) return
  errorNotified = true
  emit('error', message)
}

function reportPayPalError(err: unknown) {
  // 原始错误体比映射后的文案信息量大得多，排查时需要。
  console.error('[PayPal] card payment failed', err)
  reportError(resolvePayPalSdkError(err, t))
}

const FIELD_SELECTORS = [
  '#paypal-card-name',
  '#paypal-card-number',
  '#paypal-card-expiry',
  '#paypal-card-cvv'
]

/** 换新 PayPal 订单时会重新 render，先拆掉上一轮的 iframe 免得叠加。 */
function teardownFields() {
  for (const field of renderedFields) {
    try {
      field.close()
    } catch {
      // SDK 已卸载时 close 会抛，此时容器清空即可。
    }
  }
  renderedFields = []
  for (const selector of FIELD_SELECTORS) {
    const host = document.querySelector(selector)
    if (host) host.innerHTML = ''
  }
  cardFields.value = null
}

async function initCardFields() {
  loading.value = true
  ready.value = false
  errorNotified = false
  teardownFields()

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
      style: readPayPalFieldStyle(),
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
      onError: (err: unknown) => {
        if (settled) return
        paying.value = false
        reportPayPalError(err)
      }
    })

    if (!fields.isEligible()) {
      reportError(t('portal.buy.cardNotEligible'))
      return
    }

    cardFields.value = fields
    const instances = [
      fields.NameField({}),
      fields.NumberField({}),
      fields.ExpiryField({}),
      fields.CVVField({})
    ]
    renderedFields = instances
    await Promise.all(instances.map((field, i) => field.render(FIELD_SELECTORS[i])))

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
  } catch (err) {
    if (settled) return
    paying.value = false
    reportPayPalError(err)
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

// iframe 内的样式在初始化时就固定了，切主题必须重建。
// 重建会清空已填的卡号，所以支付进行中一律跳过，等这一轮结束。
watch(
  () => theme.mode,
  () => {
    if (!props.paypalOrderId || paying.value || settled || destroyed) return
    initCardFields()
  }
)

onMounted(() => {
  if (props.paypalOrderId) {
    initCardFields()
  }
})

onBeforeUnmount(() => {
  destroyed = true
  teardownFields()
})

defineExpose({ submitPayment })
</script>

<template>
  <LoadingOverlay :loading="loading">
    <div class="space-y-4">
      <div class="space-y-2">
        <Label for="paypal-card-number">{{ t('portal.buy.cardNumber') }}</Label>
        <div
          id="paypal-card-number"
          class="h-11 rounded-md border border-input bg-background px-3 py-2 transition-colors focus-within:border-ring focus-within:ring-[3px] focus-within:ring-ring/30"
        />
      </div>
      <div class="space-y-2">
        <Label for="paypal-card-name">{{ t('portal.buy.cardName') }}</Label>
        <div
          id="paypal-card-name"
          class="h-11 rounded-md border border-input bg-background px-3 py-2 transition-colors focus-within:border-ring focus-within:ring-[3px] focus-within:ring-ring/30"
        />
      </div>
      <div class="grid grid-cols-2 gap-4">
        <div class="space-y-2">
          <Label for="paypal-card-expiry">{{ t('portal.buy.cardExpiry') }}</Label>
          <div
            id="paypal-card-expiry"
            class="h-11 rounded-md border border-input bg-background px-3 py-2 transition-colors focus-within:border-ring focus-within:ring-[3px] focus-within:ring-ring/30"
          />
        </div>
        <div class="space-y-2">
          <Label for="paypal-card-cvv">{{ t('portal.buy.cardCvv') }}</Label>
          <div
            id="paypal-card-cvv"
            class="h-11 rounded-md border border-input bg-background px-3 py-2 transition-colors focus-within:border-ring focus-within:ring-[3px] focus-within:ring-ring/30"
          />
        </div>
      </div>

      <Button class="h-11 w-full text-base" :disabled="!ready || paying" @click="submitPayment">
        {{ t('portal.buy.payAmount', { amount: currencySymbol(currency) + formatPrice(amount) }) }}
      </Button>
      <p class="text-center text-xs text-muted-foreground">
        {{ t('portal.buy.poweredByPayPal') }}
      </p>
    </div>
  </LoadingOverlay>
</template>
