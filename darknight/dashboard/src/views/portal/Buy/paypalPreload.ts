import { loadScript } from '@paypal/paypal-js'
import { fetchPayPalConfig } from '@/api/portal/orders'

let preloadPromise: Promise<void> | null = null

/** 提前加载 PayPal SDK，进入付款页时 iframe 可尽快渲染。 */
export function preloadPayPalSdk(): Promise<void> {
  if (!preloadPromise) {
    preloadPromise = (async () => {
      const config = await fetchPayPalConfig()
      if (!config.enabled || !config.client_id) return
      await loadScript({
        clientId: config.client_id,
        components: 'card-fields',
        currency: config.currency
      })
    })().catch(() => {
      preloadPromise = null
    })
  }
  return preloadPromise
}

export function resetPayPalSdkPreload() {
  preloadPromise = null
}
