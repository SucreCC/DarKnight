<script setup lang="ts">
import { toRef } from 'vue'
import { useI18n } from 'vue-i18n'
import { type PortalOrder } from '@/api/portal/orders'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import LoadingOverlay from '@/components/LoadingOverlay/index.vue'
import { currencySymbol, formatPrice } from '../plans'
import { usePayPalCardFields } from './usePayPalCardFields'

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

const { loading, paying, ready, submitPayment } = usePayPalCardFields({
  orderId: toRef(props, 'orderId'),
  paypalOrderId: toRef(props, 'paypalOrderId'),
  onSuccess: (order) => emit('success', order),
  onError: (message) => emit('error', message)
})
</script>

<template>
  <LoadingOverlay :loading="loading">
    <div class="space-y-4">
      <div class="space-y-2">
        <Label for="paypal-card-number">{{ t('portal.buy.cardNumber') }}</Label>
        <div class="paypal-field-wrap">
          <div id="paypal-card-number" class="paypal-field-mount" />
        </div>
      </div>

      <div class="space-y-2">
        <Label for="paypal-card-name">{{ t('portal.buy.cardName') }}</Label>
        <div class="paypal-field-wrap">
          <div id="paypal-card-name" class="paypal-field-mount" />
        </div>
      </div>

      <div class="grid grid-cols-2 gap-4">
        <div class="space-y-2">
          <Label for="paypal-card-expiry">{{ t('portal.buy.cardExpiry') }}</Label>
          <div class="paypal-field-wrap">
            <div id="paypal-card-expiry" class="paypal-field-mount" />
          </div>
        </div>
        <div class="space-y-2">
          <Label for="paypal-card-cvv">{{ t('portal.buy.cardCvv') }}</Label>
          <div class="paypal-field-wrap">
            <div id="paypal-card-cvv" class="paypal-field-mount" />
          </div>
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

<style scoped>
.paypal-field-wrap {
  height: 2.75rem;
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
