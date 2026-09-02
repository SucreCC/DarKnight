import { http } from '@/config/axios'

export interface PortalProfile {
  email: string
  notify_expire_email: boolean
  notify_traffic_email: boolean
}

export function fetchPortalProfile() {
  return http<PortalProfile>('/profile')
}

export function updatePortalProfile(
  body: Partial<Pick<PortalProfile, 'notify_expire_email' | 'notify_traffic_email'>>
) {
  return http<PortalProfile>('/profile', { method: 'PATCH', body })
}

export function changePortalPassword(body: { old_password: string; new_password: string }) {
  return http('/profile/change-password', { method: 'POST', body })
}

export function revokePortalSubscription() {
  return http('/profile/revoke-subscription', { method: 'POST' })
}
