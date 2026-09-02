import { createRouter, createWebHistory } from 'vue-router'
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

function resolveHistoryBase(): string {
  const base = import.meta.env.BASE_URL
  if (!base || base === './') return '/'
  return base
}

const router = createRouter({
  history: createWebHistory(resolveHistoryBase()),
  routes
})

export default router
