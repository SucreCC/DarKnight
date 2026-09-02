import type { RouteRecordRaw } from 'vue-router'

export const portalRoutes: RouteRecordRaw[] = [
  {
    path: '/portal/login',
    name: 'portal-login',
    redirect: (to) => ({ name: 'login', query: to.query }),
    meta: { public: true, zone: 'auth', authType: 'user' }
  },
  {
    path: '/portal/register',
    name: 'portal-register',
    component: () => import('@/views/portal/Register/index.vue'),
    meta: { public: true, zone: 'auth', authType: 'user' }
  },
  {
    path: '/portal/orders/:orderId',
    name: 'portal-order-detail',
    component: () => import('@/views/portal/Orders/Detail.vue'),
    meta: {
      title: 'portal.buy.orderDetailTitle',
      zone: 'portal',
      authType: 'user',
      hideInMenu: true
    }
  },
  {
    path: '/portal/tickets/:ticketId',
    name: 'portal-ticket-detail',
    component: () => import('@/views/portal/Tickets/Detail.vue'),
    meta: {
      title: 'portal.tickets.detailTitle',
      zone: 'portal',
      authType: 'user',
      hideInMenu: true
    }
  },
  {
    path: '/portal',
    component: () => import('@/layout/UserLayout/index.vue'),
    meta: { zone: 'portal', authType: 'user' },
    redirect: { name: 'portal-dashboard' },
    children: [
      {
        path: 'dashboard',
        name: 'portal-dashboard',
        component: () => import('@/views/portal/Dashboard/index.vue'),
        meta: { title: 'portal.menu.dashboard', icon: 'Gauge', authType: 'user' }
      },
      {
        path: 'docs',
        name: 'portal-docs',
        component: () => import('@/views/portal/Docs/index.vue'),
        meta: { title: 'portal.menu.docs', icon: 'FileText', authType: 'user' }
      },
      {
        path: 'docs/:id',
        name: 'portal-docs-detail',
        component: () => import('@/views/portal/Docs/Detail.vue'),
        meta: { title: 'portal.menu.docs', authType: 'user', hideInMenu: true }
      },
      {
        path: 'buy',
        name: 'portal-buy',
        component: () => import('@/views/portal/Buy/index.vue'),
        meta: {
          title: 'portal.menu.buySubscription',
          icon: 'ShoppingCart',
          authType: 'user',
          group: 'portal.menu.subscription'
        }
      },
      {
        path: 'buy/:planId',
        name: 'portal-buy-configure',
        component: () => import('@/views/portal/Buy/Configure.vue'),
        meta: {
          title: 'portal.buy.configureTitle',
          authType: 'user',
          hideInMenu: true
        }
      },
      {
        path: 'nodes',
        name: 'portal-nodes',
        component: () => import('@/views/portal/Placeholder/index.vue'),
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
        component: () => import('@/views/portal/Orders/index.vue'),
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
        component: () => import('@/views/portal/Invite/index.vue'),
        meta: {
          title: 'portal.menu.invite',
          icon: 'UserPlus',
          authType: 'user',
          group: 'portal.menu.finance'
        }
      },
      {
        path: 'profile',
        name: 'portal-profile',
        component: () => import('@/views/portal/Profile/index.vue'),
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
        component: () => import('@/views/portal/Tickets/index.vue'),
        meta: {
          title: 'portal.menu.tickets',
          icon: 'Headset',
          authType: 'user',
          group: 'portal.menu.user'
        }
      },
      {
        path: 'traffic',
        name: 'portal-traffic',
        component: () => import('@/views/portal/Placeholder/index.vue'),
        meta: {
          title: 'portal.menu.traffic',
          icon: 'Activity',
          authType: 'user',
          group: 'portal.menu.user'
        }
      }
    ]
  }
]
