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
        path: 'pricing',
        name: 'site-pricing',
        component: () => import('@/views/site/Pricing/index.vue'),
        meta: { title: 'site.menu.pricing', public: true, zone: 'site' }
      },
      {
        path: 'faq',
        name: 'site-faq',
        component: () => import('@/views/site/Faq/index.vue'),
        meta: { title: 'site.menu.faq', public: true, zone: 'site' }
      },
      {
        path: 'guides',
        name: 'site-guides',
        component: () => import('@/views/site/Guides/index.vue'),
        meta: { title: 'site.menu.guides', public: true, zone: 'site' }
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
