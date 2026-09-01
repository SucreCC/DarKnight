import type { RouteRecordRaw } from 'vue-router'

export const adminRoutes: RouteRecordRaw[] = [
  {
    path: '/admin',
    component: () => import('@/layout/index.vue'),
    meta: { zone: 'admin', authType: 'admin' },
    redirect: { name: 'users' },
    children: [
      {
        path: 'users',
        name: 'users',
        component: () => import('@/views/admin/User/index.vue'),
        meta: { title: 'users', icon: 'Users', authType: 'admin' }
      },
      {
        path: 'nodes',
        name: 'nodes',
        component: () => import('@/views/admin/Node/index.vue'),
        meta: { title: 'header.nodeSettings', icon: 'Network', authType: 'admin' }
      },
      {
        path: 'hosts',
        name: 'hosts',
        component: () => import('@/views/admin/Host/index.vue'),
        meta: { title: 'header.hostSettings', icon: 'Link', authType: 'admin' }
      },
      {
        path: 'settings',
        name: 'settings',
        component: () => import('@/views/admin/Setting/index.vue'),
        meta: { title: 'core.title', icon: 'Settings', authType: 'admin' }
      }
    ]
  },
  { path: '/users', redirect: { name: 'users' } },
  { path: '/nodes', redirect: { name: 'nodes' } },
  { path: '/hosts', redirect: { name: 'hosts' } },
  { path: '/settings', redirect: { name: 'settings' } }
]
