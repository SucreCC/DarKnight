const USER_TOKEN_KEY = 'user_token'

export const getUserToken = (): string | null => {
  return localStorage.getItem(USER_TOKEN_KEY)
}

export const setUserToken = (token: string): void => {
  localStorage.setItem(USER_TOKEN_KEY, token)
}

export const removeUserToken = (): void => {
  localStorage.removeItem(USER_TOKEN_KEY)
}

/** True when the current page is under the portal zone (history or hash mode). */
export function isPortalRoute(): boolean {
  // createWebHistory uses /portal/... ; keep hash fallback for older builds.
  if (window.location.hash.startsWith('#/portal')) return true
  return /(?:^|\/)portal(?:\/|$)/.test(window.location.pathname)
}
