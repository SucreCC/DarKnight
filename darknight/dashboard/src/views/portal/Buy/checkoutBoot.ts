import { ref } from 'vue'

/** 下单 → 支付页 PayPal 字段就绪前，跨路由保持全页 loading */
export const isCheckoutBooting = ref(false)

export function startCheckoutBoot() {
  isCheckoutBooting.value = true
}

export function finishCheckoutBoot() {
  isCheckoutBooting.value = false
}
