import { createRouter, createWebHashHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

export const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/Login/index.vue'),
    meta: { public: true }
  },
  {
    path: '/',
    component: () => import('@/layout/index.vue'),
    redirect: { name: 'users' },
    children: [
      {
        path: 'users',
        name: 'users',
        component: () => import('@/views/User/index.vue'),
        meta: { title: 'users', icon: 'User' }
      },
      {
        path: 'nodes',
        name: 'nodes',
        component: () => import('@/views/Node/index.vue'),
        meta: { title: 'header.nodeSettings', icon: 'Connection' }
      },
      {
        path: 'hosts',
        name: 'hosts',
        component: () => import('@/views/Host/index.vue'),
        meta: { title: 'header.hostSettings', icon: 'Link' }
      },
      {
        path: 'settings',
        name: 'settings',
        component: () => import('@/views/Setting/index.vue'),
        meta: { title: 'core.title', icon: 'Setting' }
      }
    ]
  },
  { path: '/:pathMatch(.*)*', redirect: { name: 'users' } }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

export default router
