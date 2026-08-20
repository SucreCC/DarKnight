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
        path: 'docs',
        name: 'site-docs',
        component: () => import('@/views/site/Docs/index.vue'),
        meta: { title: 'site.menu.docs', public: true, zone: 'site' }
      },
      {
        path: 'docs/:id',
        name: 'site-docs-detail',
        component: () => import('@/views/site/Docs/Detail.vue'),
        meta: { title: 'site.menu.docs', public: true, zone: 'site', hideInMenu: true }
      }
    ]
  }
]
