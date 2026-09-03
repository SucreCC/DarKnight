import { computed, type ComputedRef } from 'vue'
import { useHead, useSeoMeta } from '@unhead/vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import type { LocaleCode } from '@/plugins/vueI18n'
import {
  SITE_NAME,
  SITE_URL,
  buildAlternateUrls,
  buildCanonicalUrl
} from '@/config/seo'

export interface PageSeoOptions {
  titleKey: string
  descriptionKey?: string
  keywordsKey?: string
  noindex?: boolean
  withHreflang?: boolean
  withFaqSchema?: boolean
  /** FAQ schema key pattern. Default uses site.home.faq{n}Q / site.home.faq{n}A */
  faqSchema?: {
    count: number
    questionKey: (index: number) => string
    answerKey: (index: number) => string
  }
}

export function usePageSeo(options: PageSeoOptions): void {
  const { t, locale } = useI18n()
  const route = useRoute()

  const title = computed(() => t(options.titleKey))
  const description = computed(() =>
    options.descriptionKey ? t(options.descriptionKey) : t('site.seo.description')
  )
  const keywords = computed(() =>
    options.keywordsKey ? t(options.keywordsKey) : t('site.seo.keywords')
  )
  const canonical = computed(() => buildCanonicalUrl(route.path, locale.value as LocaleCode))
  const ogImage = `${SITE_URL}/statics/logo.png`
  const robots = computed(() => (options.noindex ? 'noindex, nofollow' : 'index, follow'))

  useSeoMeta({
    title,
    description,
    robots,
    ogTitle: title,
    ogDescription: description,
    ogUrl: canonical,
    ogType: 'website',
    ogSiteName: SITE_NAME,
    ogImage,
    ogLocale: computed(() => (locale.value === 'zh' ? 'zh_CN' : locale.value)),
    twitterCard: 'summary',
    twitterTitle: title,
    twitterDescription: description,
    twitterImage: ogImage
  })

  const linkTags: ComputedRef<
    Array<{ rel: 'canonical' | 'alternate'; href: string; hreflang?: string }>
  > = computed(() => {
    const links: Array<{ rel: 'canonical' | 'alternate'; href: string; hreflang?: string }> = [
      { rel: 'canonical', href: canonical.value }
    ]
    if (options.withHreflang) {
      links.push(
        ...buildAlternateUrls(route.path).map((alt) => ({
          rel: 'alternate' as const,
          hreflang: alt.hreflang,
          href: alt.href
        })),
        {
          rel: 'alternate' as const,
          hreflang: 'x-default',
          href: `${SITE_URL}${route.path === '/' ? '' : route.path}`
        }
      )
    }
    return links
  })

  useHead({
    meta: computed(() => [{ name: 'keywords', content: keywords.value }]),
    link: linkTags,
    script: computed(() => {
      if (!options.withFaqSchema) return []

      const faq =
        options.faqSchema ??
        (        {
          count: 7,
          questionKey: (i: number) => `site.home.faq${i}Q`,
          answerKey: (i: number) => `site.home.faq${i}A`
        } as const)

      return [
        {
          type: 'application/ld+json',
          innerHTML: JSON.stringify({
            '@context': 'https://schema.org',
            '@graph': [
              {
                '@type': 'Organization',
                name: SITE_NAME,
                alternateName: ['DarKnight', 'darkight', 'darknight'],
                url: SITE_URL,
                logo: ogImage,
                description: description.value
              },
              {
                '@type': 'WebSite',
                name: SITE_NAME,
                alternateName: ['DarKnight', 'darkight', 'darknight'],
                url: SITE_URL,
                description: description.value,
                inLanguage: locale.value === 'zh' ? 'zh-CN' : locale.value
              },
              {
                '@type': 'FAQPage',
                mainEntity: Array.from({ length: faq.count }, (_, idx) => {
                  const i = idx + 1
                  return {
                    '@type': 'Question',
                    name: t(faq.questionKey(i)),
                    acceptedAnswer: {
                      '@type': 'Answer',
                      text: t(faq.answerKey(i))
                    }
                  }
                })
              }
            ]
          })
        }
      ]
    })
  })
}
