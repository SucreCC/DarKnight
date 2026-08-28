<script setup lang="ts">
import { Loader2 } from 'lucide-vue-next'
import { computed, ref, toRef, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import { type PortalOrder } from '@/api/portal/orders'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { currencySymbol, formatPrice } from '../plans'
import { usePayPalCardFields } from './usePayPalCardFields'

const props = withDefaults(
  defineProps<{
    orderId: string
    paypalOrderId: string
    amount: number
    currency: string
    bootOverlay?: boolean
  }>(),
  { bootOverlay: true }
)

const emit = defineEmits<{
  success: [order: PortalOrder]
  error: [message: string, refreshOrder?: boolean]
  ready: []
}>()

const { t } = useI18n()
const errorMessage = ref('')

function handleError(message: string, refreshOrder?: boolean) {
  errorMessage.value = message
  toast.error(message)
  emit('error', message, refreshOrder)
}

const { paying, ready, submitPayment } = usePayPalCardFields({
  orderId: toRef(props, 'orderId'),
  paypalOrderId: toRef(props, 'paypalOrderId'),
  onSuccess: (order) => {
    errorMessage.value = ''
    emit('success', order)
  },
  onError: handleError
})

const showForm = computed(() => ready.value)
const showBoot = computed(() => props.bootOverlay && !ready.value && !errorMessage.value)

watch(ready, (isReady) => {
  if (isReady) emit('ready')
})

async function onPayClick() {
  errorMessage.value = ''
  await submitPayment()
}
</script>

<template>
  <div class="relative min-h-[320px]">
    <div
      v-if="showBoot"
      class="absolute inset-0 z-20 flex flex-col items-center justify-center gap-3 bg-card"
    >
      <Loader2 class="size-8 animate-spin text-primary" />
      <p class="text-sm text-muted-foreground">{{ t('portal.buy.paymentLoading') }}</p>
    </div>

    <Alert v-if="errorMessage" variant="destructive" class="relative z-10 mb-4">
      <AlertDescription>{{ errorMessage }}</AlertDescription>
    </Alert>

    <!-- 挂载层：就绪前不可见，避免灰色占位框先露出 -->
    <div
      class="space-y-4"
      :class="
        showForm
          ? 'relative opacity-100'
          : 'pointer-events-none invisible absolute inset-0 -z-10 opacity-0'
      "
      :aria-hidden="!showForm"
    >
      <div class="space-y-2">
        <Label for="paypal-card-number">{{ t('portal.buy.cardNumber') }}</Label>
        <div class="paypal-field-wrap" :class="{ 'paypal-field-wrap--ready': showForm }">
          <div id="paypal-card-number" class="paypal-field-mount" />
        </div>
      </div>

      <div class="space-y-2">
        <Label for="paypal-card-name">{{ t('portal.buy.cardName') }}</Label>
        <div class="paypal-field-wrap" :class="{ 'paypal-field-wrap--ready': showForm }">
          <div id="paypal-card-name" class="paypal-field-mount" />
        </div>
      </div>

      <div class="grid grid-cols-2 gap-4">
        <div class="space-y-2">
          <Label for="paypal-card-expiry">{{ t('portal.buy.cardExpiry') }}</Label>
          <div class="paypal-field-wrap" :class="{ 'paypal-field-wrap--ready': showForm }">
            <div id="paypal-card-expiry" class="paypal-field-mount" />
          </div>
        </div>
        <div class="space-y-2">
          <Label for="paypal-card-cvv">{{ t('portal.buy.cardCvv') }}</Label>
          <div class="paypal-field-wrap" :class="{ 'paypal-field-wrap--ready': showForm }">
            <div id="paypal-card-cvv" class="paypal-field-mount" />
          </div>
        </div>
      </div>

      <Button class="h-11 w-full text-base" :disabled="!ready || paying" @click="onPayClick">
        <Loader2 v-if="paying" class="me-2 size-4 animate-spin" />
        {{
          paying
            ? t('portal.buy.paying')
            : t('portal.buy.payAmount', { amount: currencySymbol(currency) + formatPrice(amount) })
        }}
      </Button>
      <p class="text-center text-xs text-muted-foreground">
        {{ t('portal.buy.poweredByPayPal') }}
      </p>
    </div>
  </div>
</template>

<style scoped>
.paypal-field-wrap {
  height: 2.75rem;
  border-radius: calc(var(--radius) - 2px);
}

.paypal-field-wrap--ready {
  background-color: var(--paypal-field-bg, #f4f4f5);
}

.paypal-field-mount {
  width: 100%;
  height: 100%;
}

.paypal-field-mount :deep(div) {
  width: 100%;
  height: 100%;
}

.paypal-field-mount :deep(iframe) {
  display: block;
  width: 100%;
  height: 100%;
  border: 0;
}
</style>
