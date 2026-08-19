import router from '@/router'
import { getAccessToken } from '@/utils/auth'
import { getUserToken } from '@/utils/userAuth'

router.beforeEach((to) => {
  const authType = (to.meta.authType as 'admin' | 'user' | undefined) ?? 'admin'
  const isPublic = to.meta.public === true

  if (authType === 'user') {
    const hasUserToken = !!getUserToken()
    if (!isPublic && !hasUserToken) {
      return { name: 'portal-login', query: { redirect: to.fullPath } }
    }
    if ((to.name === 'portal-login' || to.name === 'portal-register') && hasUserToken) {
      return { name: 'portal-dashboard' }
    }
    return true
  }

  const hasToken = !!getAccessToken()
  if (!isPublic && !hasToken) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  if (to.name === 'login' && hasToken) {
    return { name: 'users' }
  }
  return true
})
