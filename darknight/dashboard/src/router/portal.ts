import type { RouteRecordRaw } from 'vue-router'

export const portalRoutes: RouteRecordRaw[] = [
  {
    path: '/portal/login',
    name: 'portal-login',
    component: () => import('@/views/Portal/Login/index.vue'),
    meta: { public: true, authType: 'user' }
  },
  {
    path: '/portal/register',
    name: 'portal-register',
    component: () => import('@/views/Portal/Register/index.vue'),
    meta: { public: true, authType: 'user' }
  },
  {
    path: '/portal',
    component: () => import('@/layout/UserLayout/index.vue'),
    meta: { authType: 'user' },
    redirect: { name: 'portal-dashboard' },
    children: [
      {
        path: 'dashboard',
        name: 'portal-dashboard',
        component: () => import('@/views/Portal/Dashboard/index.vue'),
        meta: { title: 'portal.menu.dashboard', icon: 'Odometer', authType: 'user' }
      },
      {
        path: 'docs',
        name: 'portal-docs',
        component: () => import('@/views/Portal/Docs/index.vue'),
        meta: { title: 'portal.menu.docs', icon: 'Document', authType: 'user' }
      },
      {
        path: 'docs/:id',
        name: 'portal-docs-detail',
        component: () => import('@/views/Portal/Docs/Detail.vue'),
        meta: { title: 'portal.menu.docs', authType: 'user', hideInMenu: true }
      },
      {
        path: 'buy',
        name: 'portal-buy',
        component: () => import('@/views/Portal/Placeholder/index.vue'),
        meta: {
          title: 'portal.menu.buySubscription',
          icon: 'ShoppingCart',
          authType: 'user',
          group: 'portal.menu.subscription'
        }
      },
      {
        path: 'nodes',
        name: 'portal-nodes',
        component: () => import('@/views/Portal/Placeholder/index.vue'),
        meta: {
          title: 'portal.menu.nodeStatus',
          icon: 'Monitor',
          authType: 'user',
          group: 'portal.menu.subscription'
        }
      },
      {
        path: 'orders',
        name: 'portal-orders',
        component: () => import('@/views/Portal/Placeholder/index.vue'),
        meta: {
          title: 'portal.menu.orders',
          icon: 'List',
          authType: 'user',
          group: 'portal.menu.finance'
        }
      },
      {
        path: 'invite',
        name: 'portal-invite',
        component: () => import('@/views/Portal/Placeholder/index.vue'),
        meta: {
          title: 'portal.menu.invite',
          icon: 'UserFilled',
          authType: 'user',
          group: 'portal.menu.finance'
        }
      },
      {
        path: 'profile',
        name: 'portal-profile',
        component: () => import('@/views/Portal/Placeholder/index.vue'),
        meta: {
          title: 'portal.menu.profile',
          icon: 'User',
          authType: 'user',
          group: 'portal.menu.user'
        }
      },
      {
        path: 'tickets',
        name: 'portal-tickets',
        component: () => import('@/views/Portal/Placeholder/index.vue'),
        meta: {
          title: 'portal.menu.tickets',
          icon: 'Service',
          authType: 'user',
          group: 'portal.menu.user'
        }
      },
      {
        path: 'traffic',
        name: 'portal-traffic',
        component: () => import('@/views/Portal/Placeholder/index.vue'),
        meta: {
          title: 'portal.menu.traffic',
          icon: 'DataLine',
          authType: 'user',
          group: 'portal.menu.user'
        }
      }
    ]
  }
]
