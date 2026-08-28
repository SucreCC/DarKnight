import { onBeforeUnmount, onMounted, ref, watch, type Ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { loadScript, type PayPalCardFieldsComponent } from '@paypal/paypal-js'
import { capturePortalOrder, fetchPayPalConfig, type PortalOrder } from '@/api/portal/orders'
import { resolvePayPalSdkError, resolvePortalApiError } from '@/utils/portalError'
import { useThemeStore } from '@/store/modules/theme'
import { readPayPalFieldStyle, readPayPalNumberFieldStyle } from './paypalFieldStyle'
import { preloadPayPalSdk } from '../paypalPreload'

const FIELD_IDS = [
  'paypal-card-number',
  'paypal-card-name',
  'paypal-card-expiry',
  'paypal-card-cvv'
] as const

const IFRAME_POLL_MS = 50
const IFRAME_WAIT_MS = 20_000
const IFRAME_LOAD_MS = 8_000

function getMountIframe(id: (typeof FIELD_IDS)[number]): HTMLIFrameElement | null {
  return document.getElementById(id)?.querySelector('iframe') ?? null
}

function waitForIframeLoad(iframe: HTMLIFrameElement): Promise<void> {
  return new Promise((resolve) => {
    const done = () => resolve()
    iframe.addEventListener('load', done, { once: true })
    window.setTimeout(done, IFRAME_LOAD_MS)
  })
}

/** render() 返回后 iframe 可能尚未插入 DOM，需轮询直到四个字段均就绪。 */
async function waitForAllFieldIframes(generation: number, isStale: () => boolean): Promise<boolean> {
  const deadline = Date.now() + IFRAME_WAIT_MS

  while (Date.now() < deadline) {
    if (isStale()) return false

    const iframes = FIELD_IDS.map(getMountIframe)
    const allMounted = iframes.every(
      (iframe) => iframe && iframe.offsetWidth > 0 && iframe.offsetHeight > 0
    )

    if (allMounted) {
      await Promise.all(iframes.map((iframe) => waitForIframeLoad(iframe!)))
      if (isStale()) return false
      await new Promise<void>((resolve) =>
        requestAnimationFrame(() => requestAnimationFrame(() => resolve()))
      )
      return FIELD_IDS.every((id) => getMountIframe(id) !== null)
    }

    await new Promise((resolve) => window.setTimeout(resolve, IFRAME_POLL_MS))
  }

  return false
}

export function usePayPalCardFields(options: {
  orderId: Ref<string>
  paypalOrderId: Ref<string>
  onSuccess: (order: PortalOrder) => void
  onError: (message: string, refreshOrder?: boolean) => void
  onReady?: () => void
}) {
  const { t } = useI18n()
  const theme = useThemeStore()

  const loading = ref(true)
  const paying = ref(false)
  const ready = ref(false)
  const cardFields = ref<PayPalCardFieldsComponent | null>(null)

  let destroyed = false
  let settled = false
  let renderedFields: { close: () => void }[] = []
  let fieldsGeneration = 0
  let themeRebuildDeferred = false
  let submitGeneration = 0
  let captureInFlight = false
  let submitTimeoutId: ReturnType<typeof setTimeout> | null = null
  /** 同一次 submit：onError 与 submit() reject 可能各报一次，只提示一次。 */
  let submitErrored = false

  function resetSubmitErrorState() {
    submitErrored = false
  }

  function clearSubmitTimeout() {
    if (submitTimeoutId !== null) {
      window.clearTimeout(submitTimeoutId)
      submitTimeoutId = null
    }
  }

  function notifyError(message: string, refreshOrder = true) {
    if (settled || destroyed) return
    options.onError(message, refreshOrder)
  }

  function reportSubmitError(err: unknown) {
    if (submitErrored || settled || destroyed) return
    submitErrored = true
    console.error('[PayPal] card payment failed', err)
    notifyError(resolvePayPalSdkError(err, t))
  }

  async function finalizeCapture(attempt: number): Promise<void> {
    if (captureInFlight || settled || destroyed || attempt !== submitGeneration) return
    captureInFlight = true
    paying.value = true
    try {
      const { order } = await capturePortalOrder(options.orderId.value)
      if (attempt !== submitGeneration || settled || destroyed) return
      settled = true
      clearSubmitTimeout()
      options.onSuccess(order)
    } catch (err) {
      if (attempt !== submitGeneration || settled || destroyed) return
      paying.value = false
      notifyError(resolvePortalApiError(err, t))
    } finally {
      captureInFlight = false
    }
  }

  function teardownFields() {
    clearSubmitTimeout()
    for (const field of renderedFields) {
      try {
        field.close()
      } catch {
        // SDK 已卸载时 close 会抛，此时容器清空即可。
      }
    }
    renderedFields = []
    for (const id of FIELD_IDS) {
      const host = document.getElementById(id)
      if (host) host.innerHTML = ''
    }
    cardFields.value = null
  }

  async function initCardFields() {
    if (paying.value || settled) return

    themeRebuildDeferred = false
    const generation = ++fieldsGeneration
    loading.value = true
    ready.value = false
    teardownFields()

    try {
      await preloadPayPalSdk()
      const config = await fetchPayPalConfig()
      if (generation !== fieldsGeneration || destroyed) return
      if (!config.enabled || !config.client_id) {
        notifyError(t('portal.buy.paypalNotConfigured'), false)
        return
      }

      const paypal = await loadScript({
        clientId: config.client_id,
        components: 'card-fields',
        currency: config.currency
      })

      if (generation !== fieldsGeneration || destroyed) return
      if (!paypal?.CardFields) {
        notifyError(t('portal.buy.paypalLoadFailed'), false)
        return
      }

      const fields = paypal.CardFields({
        style: readPayPalFieldStyle() as never,
        createOrder: () => Promise.resolve(options.paypalOrderId.value),
        onApprove: async () => {
          await finalizeCapture(submitGeneration)
        },
        onError: (err: unknown) => {
          if (settled) return
          clearSubmitTimeout()
          paying.value = false
          reportSubmitError(err)
        }
      })

      if (generation !== fieldsGeneration || destroyed) return

      if (!fields.isEligible()) {
        notifyError(t('portal.buy.cardNotEligible'), false)
        return
      }

      cardFields.value = fields
      const instances = [
        fields.NumberField({
          placeholder: t('portal.buy.cardNumber'),
          style: readPayPalNumberFieldStyle() as never
        }),
        fields.NameField({ placeholder: t('portal.buy.cardName') }),
        fields.ExpiryField({ placeholder: 'MM / YY' }),
        fields.CVVField({ placeholder: t('portal.buy.cardCvv') })
      ]
      renderedFields = instances
      await Promise.all(instances.map((field, i) => field.render(`#${FIELD_IDS[i]}`)))

      const isStale = () => generation !== fieldsGeneration || destroyed
      const injected = await waitForAllFieldIframes(generation, isStale)
      if (isStale()) return
      if (!injected) {
        notifyError(t('portal.buy.paypalLoadFailed'), false)
        return
      }

      ready.value = true
      options.onReady?.()
    } catch {
      if (generation !== fieldsGeneration || destroyed) return
      notifyError(t('portal.buy.paypalLoadFailed'), false)
    } finally {
      if (generation === fieldsGeneration && !destroyed) {
        loading.value = false
      }
    }
  }

  async function submitPayment() {
    if (!cardFields.value || paying.value || settled) return

    resetSubmitErrorState()

    let state
    try {
      state = await cardFields.value.getState()
    } catch (err) {
      reportSubmitError(err)
      return
    }

    if (!state.isFormValid) {
      notifyError(t('portal.buy.cardFormIncomplete'), false)
      return
    }

    const attempt = ++submitGeneration
    submitErrored = false
    paying.value = true
    clearSubmitTimeout()

    try {
      await cardFields.value.submit()
      if (settled || attempt !== submitGeneration) return
      await finalizeCapture(attempt)
    } catch (err) {
      if (settled || attempt !== submitGeneration) return
      clearSubmitTimeout()
      paying.value = false
      reportSubmitError(err)
      return
    }

    submitTimeoutId = window.setTimeout(() => {
      if (attempt !== submitGeneration || settled || destroyed || !paying.value) return
      paying.value = false
      notifyError(t('portal.buy.paymentFailed'))
    }, 30_000)
  }

  watch(
    () => options.paypalOrderId.value,
    (id, prev) => {
      if (!id) return
      // 支付失败后只换 PayPal 订单号，不重建 iframe，保留已填卡号。
      if (id !== prev && ready.value && cardFields.value) return
      if (id !== prev || !ready.value) initCardFields()
    }
  )

  watch(
    () => theme.mode,
    () => {
      if (!options.paypalOrderId.value || settled || destroyed) return
      if (paying.value) {
        themeRebuildDeferred = true
        return
      }
      initCardFields()
    }
  )

  watch(paying, (isPaying) => {
    if (isPaying || settled || destroyed || !themeRebuildDeferred) return
    themeRebuildDeferred = false
    if (options.paypalOrderId.value) initCardFields()
  })

  onMounted(() => {
    if (options.paypalOrderId.value) initCardFields()
  })

  onBeforeUnmount(() => {
    destroyed = true
    teardownFields()
  })

  return { loading, paying, ready, submitPayment }
}
