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

export function isPortalRoute(): boolean {
  return window.location.hash.startsWith('#/portal')
}
