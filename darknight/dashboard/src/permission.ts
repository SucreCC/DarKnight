import router from '@/router'
import { getAccessToken } from '@/utils/auth'

router.beforeEach((to) => {
  const isPublic = to.meta.public === true
  const hasToken = !!getAccessToken()
  if (!isPublic && !hasToken) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  if (to.name === 'login' && hasToken) {
    return { name: 'users' }
  }
  return true
})
