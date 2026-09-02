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
      },
      {
        path: 'privacy',
        name: 'site-privacy',
        component: () => import('@/views/site/Privacy/index.vue'),
        meta: { title: 'site.legal.privacy', public: true, zone: 'site' }
      },
      {
        path: 'terms',
        name: 'site-terms',
        component: () => import('@/views/site/Terms/index.vue'),
        meta: { title: 'site.legal.terms', public: true, zone: 'site' }
      }
    ]
  }
]
