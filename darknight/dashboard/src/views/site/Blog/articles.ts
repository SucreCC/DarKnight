export interface BlogPost {
  slug: string
  titleKey: string
  descriptionKey: string
  publishedAt: string
  updatedAt: string
  bodyKeys: string[]
}

export const BLOG_POSTS: BlogPost[] = [
  {
    slug: 'what-is-darknight-vpn',
    titleKey: 'site.blog.posts.whatIs.title',
    descriptionKey: 'site.blog.posts.whatIs.description',
    publishedAt: '2026-09-03',
    updatedAt: '2026-09-03',
    bodyKeys: [
      'site.blog.posts.whatIs.p1',
      'site.blog.posts.whatIs.p2',
      'site.blog.posts.whatIs.p3'
    ]
  },
  {
    slug: 'get-started-with-darknight',
    titleKey: 'site.blog.posts.getStarted.title',
    descriptionKey: 'site.blog.posts.getStarted.description',
    publishedAt: '2026-09-03',
    updatedAt: '2026-09-03',
    bodyKeys: [
      'site.blog.posts.getStarted.p1',
      'site.blog.posts.getStarted.p2',
      'site.blog.posts.getStarted.p3'
    ]
  },
  {
    slug: 'supported-protocols-xray',
    titleKey: 'site.blog.posts.protocols.title',
    descriptionKey: 'site.blog.posts.protocols.description',
    publishedAt: '2026-09-03',
    updatedAt: '2026-09-03',
    bodyKeys: [
      'site.blog.posts.protocols.p1',
      'site.blog.posts.protocols.p2',
      'site.blog.posts.protocols.p3'
    ]
  },
  {
    slug: 'recommended-vpn-clients',
    titleKey: 'site.blog.posts.clients.title',
    descriptionKey: 'site.blog.posts.clients.description',
    publishedAt: '2026-09-03',
    updatedAt: '2026-09-03',
    bodyKeys: [
      'site.blog.posts.clients.p1',
      'site.blog.posts.clients.p2',
      'site.blog.posts.clients.p3'
    ]
  },
  {
    slug: 'darknight-vpn-faq-deep-dive',
    titleKey: 'site.blog.posts.faqDeep.title',
    descriptionKey: 'site.blog.posts.faqDeep.description',
    publishedAt: '2026-09-03',
    updatedAt: '2026-09-03',
    bodyKeys: [
      'site.blog.posts.faqDeep.p1',
      'site.blog.posts.faqDeep.p2',
      'site.blog.posts.faqDeep.p3'
    ]
  },
  {
    slug: 'is-darknight-a-vpn',
    titleKey: 'site.blog.posts.isVpn.title',
    descriptionKey: 'site.blog.posts.isVpn.description',
    publishedAt: '2026-09-03',
    updatedAt: '2026-09-03',
    bodyKeys: [
      'site.blog.posts.isVpn.p1',
      'site.blog.posts.isVpn.p2',
      'site.blog.posts.isVpn.p3'
    ]
  }
]

export function getBlogPostBySlug(slug: string): BlogPost | undefined {
  return BLOG_POSTS.find((post) => post.slug === slug)
}

export function listBlogPosts(): BlogPost[] {
  return [...BLOG_POSTS].sort((a, b) => b.updatedAt.localeCompare(a.updatedAt))
}
