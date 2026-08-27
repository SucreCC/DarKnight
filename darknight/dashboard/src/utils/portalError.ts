import { extractErrorDetail } from '@/config/axios'

type Translate = (key: string, params?: Record<string, unknown>) => string

const DETAIL_I18N_KEYS: Record<string, string> = {
  'Email is already registered': 'portal.emailAlreadyRegistered',
  'Please wait before requesting another code': 'portal.codeCooldown',
  'Verification code expired': 'portal.codeExpired',
  'Invalid verification code': 'portal.codeInvalid',
  'Email service is not configured': 'portal.emailServiceUnavailable',
  'Registration failed, please try again': 'portal.registrationFailed',
  'PayPal payment is not configured': 'portal.buy.paypalNotConfigured',
  'Failed to create PayPal order': 'portal.buy.paypalOrderFailed',
  'Coupon is invalid or expired': 'portal.buy.couponInvalid'
}

const PAYPAL_DECLINE_PREFIX = 'PAYPAL_DECLINED:'

/**
 * PayPal 拒付原因。数字键是 processor response code（服务端 capture 返回），
 * 大写键是 PayPal 的 issue 名称（SDK 回调或错误体返回）。
 */
const PAYPAL_DECLINE_I18N_KEYS: Record<string, string> = {
  '0500': 'portal.buy.decline.doNotHonor',
  '5120': 'portal.buy.decline.insufficientFunds',
  '5400': 'portal.buy.decline.expiredCard',
  '9500': 'portal.buy.decline.fraudulent',
  '9520': 'portal.buy.decline.lostOrStolen',
  '1330': 'portal.buy.decline.invalidAccount',
  '00N7': 'portal.buy.decline.cvvFailed',
  '5180': 'portal.buy.decline.restrictedCard',
  '5100': 'portal.buy.decline.generic',
  INSTRUMENT_DECLINED: 'portal.buy.decline.generic',
  CARD_EXPIRED: 'portal.buy.decline.expiredCard',
  PAYER_ACTION_REQUIRED: 'portal.buy.decline.payerActionRequired',
  PAYER_CANNOT_PAY: 'portal.buy.decline.restrictedCard',
  TRANSACTION_REFUSED: 'portal.buy.decline.generic',
  PAYEE_NOT_ENABLED_FOR_CARD_PROCESSING: 'portal.buy.decline.cardNotEnabled'
}

export function resolvePayPalDeclineMessage(code: string, t: Translate): string {
  const normalized = code.trim().toUpperCase()
  const key = PAYPAL_DECLINE_I18N_KEYS[normalized]
  if (key) return t(key)
  return t('portal.buy.decline.unknown', { code: normalized })
}

function stringifyError(err: unknown): string {
  if (typeof err === 'string') return err
  if (err instanceof Error) return err.message || err.name
  if (err && typeof err === 'object') {
    const obj = err as Record<string, unknown>
    // PayPal SDK 常把有用信息放在这些字段里，优先取，避免整包 JSON 淹没重点。
    for (const key of ['message', 'description', 'error_description', 'name']) {
      const value = obj[key]
      if (typeof value === 'string' && value) return value
    }
    try {
      return JSON.stringify(err)
    } catch {
      return ''
    }
  }
  return err === undefined || err === null ? '' : String(err)
}

/**
 * PayPal SDK 的报错结构不稳定，可能是字符串、Error，或带 details 的对象。
 * 只把能识别的拒付原因展示给用户，其余一律给一句短提示，原始报文留在控制台。
 */
export function resolvePayPalSdkError(err: unknown, t: Translate): string {
  const issue = (err as { details?: { issue?: string }[] })?.details?.[0]?.issue
  if (issue && PAYPAL_DECLINE_I18N_KEYS[issue.trim().toUpperCase()]) {
    return resolvePayPalDeclineMessage(issue, t)
  }

  const text = stringifyError(err)
  const hit = Object.keys(PAYPAL_DECLINE_I18N_KEYS).find((code) =>
    new RegExp(`\\b${code}\\b`).test(text)
  )
  if (hit) return resolvePayPalDeclineMessage(hit, t)

  // confirm-payment-source 阶段的 422 不带字段信息时，卡号格式是合法的，
  // 但这张卡无法被受理（换卡通常能解决，重试同一张不会）。
  if (text.includes('confirm-payment-source')) {
    return t('portal.buy.decline.cardUnusable')
  }

  return t('portal.buy.paymentFailed')
}

export function resolvePortalApiError(err: unknown, t: Translate): string {
  const detail = extractErrorDetail(err)
  if (typeof detail === 'string') {
    if (detail.startsWith(PAYPAL_DECLINE_PREFIX)) {
      return resolvePayPalDeclineMessage(detail.slice(PAYPAL_DECLINE_PREFIX.length), t)
    }
    const key = DETAIL_I18N_KEYS[detail]
    if (key) return t(key)
    return detail
  }
  const status = (err as { response?: { status?: number } })?.response?.status
  if (status === 409) return t('portal.emailAlreadyRegistered')
  if (status === 429) return t('portal.codeCooldown')
  return t('portal.requestFailed')
}

export function isEmailAlreadyRegisteredError(err: unknown): boolean {
  const detail = extractErrorDetail(err)
  if (detail === 'Email is already registered') return true
  return (err as { response?: { status?: number } })?.response?.status === 409
}
