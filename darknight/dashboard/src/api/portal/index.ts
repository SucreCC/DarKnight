import { http } from '@/config/axios'
import type { PortalUser } from './types'

export function sendVerificationCode(email: string) {
  return http('/auth/send-code', { method: 'POST', body: { email } })
}

export function registerUser(body: {
  email: string
  code: string
  password: string
  invite_code?: string
}) {
  return http<{ access_token: string }>('/auth/register', { method: 'POST', body })
}

export function loginUser(email: string, password: string) {
  const formData = new FormData()
  formData.append('username', email)
  formData.append('password', password)
  formData.append('grant_type', 'password')
  return http<{ access_token: string }>('/auth/token', { method: 'POST', body: formData })
}

export function fetchPortalMe() {
  return http<PortalUser>('/auth/me')
}
