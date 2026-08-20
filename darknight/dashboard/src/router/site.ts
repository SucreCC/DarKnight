import type { RouteRecordRaw } from 'vue-router'

export const siteRoutes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('@/layout/SiteLayout/index.vue'),
    meta: { public: true, zone: 'site' },
    children: [
      {
        path: '',
        name: 'site-home',
        component: () => import('@/views/site/Home/index.vue'),
        meta: { title: 'site.menu.home', public: true, zone: 'site' }
      }
    ]
  }
]
