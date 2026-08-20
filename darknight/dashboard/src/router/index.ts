import { createRouter, createWebHashHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { siteRoutes } from './site'
import { authRoutes } from './auth'
import { adminRoutes } from './admin'
import { portalRoutes } from './portal'

export const routes: RouteRecordRaw[] = [
  ...siteRoutes,
  ...authRoutes,
  ...adminRoutes,
  ...portalRoutes,
  { path: '/:pathMatch(.*)*', redirect: { name: 'site-home' } }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

export default router
