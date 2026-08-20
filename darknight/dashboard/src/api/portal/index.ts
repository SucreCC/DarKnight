import { http } from '@/config/axios'
import type { LoginToken, PortalUser } from './types'

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

export function loginAccount(username: string, password: string) {
  const formData = new FormData()
  formData.append('username', username)
  formData.append('password', password)
  formData.append('grant_type', 'password')
  return http<LoginToken>('/auth/token', { method: 'POST', body: formData })
}

export function fetchPortalMe() {
  return http<PortalUser>('/auth/me')
}
