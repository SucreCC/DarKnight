import router from '@/router'
import { getAccessToken } from '@/utils/auth'
import { getUserToken } from '@/utils/userAuth'

router.beforeEach((to) => {
  const authType = (to.meta.authType as 'admin' | 'user' | undefined) ?? 'admin'
  const isPublic = to.meta.public === true
  const hasToken = !!getAccessToken()
  const hasUserToken = !!getUserToken()

  if (to.name === 'login' || to.name === 'portal-login') {
    if (hasToken) return { name: 'users' }
    if (hasUserToken) return { name: 'portal-dashboard' }
    if (to.name === 'portal-login') {
      return { name: 'login', query: to.query }
    }
    return true
  }

  if (authType === 'user') {
    if (!isPublic && !hasUserToken) {
      return { name: 'login', query: { redirect: to.fullPath } }
    }
    if (to.name === 'portal-register' && hasUserToken) {
      return { name: 'portal-dashboard' }
    }
    return true
  }

  if (!isPublic && !hasToken) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  return true
})
