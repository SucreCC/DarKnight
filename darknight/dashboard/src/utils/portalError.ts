import { extractErrorDetail } from '@/config/axios'

const DETAIL_I18N_KEYS: Record<string, string> = {
  'Email is already registered': 'portal.emailAlreadyRegistered',
  'Please wait before requesting another code': 'portal.codeCooldown',
  'Verification code expired': 'portal.codeExpired',
  'Invalid verification code': 'portal.codeInvalid',
  'Email service is not configured': 'portal.emailServiceUnavailable',
  'Registration failed, please try again': 'portal.registrationFailed'
}

export function resolvePortalApiError(
  err: unknown,
  t: (key: string) => string
): string {
  const detail = extractErrorDetail(err)
  if (typeof detail === 'string') {
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
