import { computed, watch } from 'vue'
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

export function useSiteSeo(): void {
  const { t, locale } = useI18n()
  const route = useRoute()

  const title = computed(() => t('site.seo.title'))
  const description = computed(() => t('site.seo.description'))
  const keywords = computed(() => t('site.seo.keywords'))
  const canonical = computed(() => buildCanonicalUrl(route.path, locale.value as LocaleCode))
  const ogImage = `${SITE_URL}/statics/logo.png`

  useSeoMeta({
    title,
    description,
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

  useHead({
    meta: computed(() => [{ name: 'keywords', content: keywords.value }]),
    link: computed(() => [
      { rel: 'canonical', href: canonical.value },
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
    ]),
    script: computed(() => [
      {
        type: 'application/ld+json',
        innerHTML: JSON.stringify({
          '@context': 'https://schema.org',
          '@graph': [
            {
              '@type': 'Organization',
              name: SITE_NAME,
              url: SITE_URL,
              logo: ogImage,
              description: description.value
            },
            {
              '@type': 'WebSite',
              name: SITE_NAME,
              url: SITE_URL,
              description: description.value,
              inLanguage: locale.value === 'zh' ? 'zh-CN' : locale.value
            },
            {
              '@type': 'FAQPage',
              mainEntity: [1, 2, 3, 4, 5].map((i) => ({
                '@type': 'Question',
                name: t(`site.home.faq${i}Q`),
                acceptedAnswer: {
                  '@type': 'Answer',
                  text: t(`site.home.faq${i}A`)
                }
              }))
            }
          ]
        })
      }
    ])
  })

  watch(
    locale,
    (value) => {
      document.documentElement.setAttribute('lang', value === 'zh' ? 'zh-CN' : value)
      document.documentElement.setAttribute('dir', value === 'fa' ? 'rtl' : 'ltr')
    },
    { immediate: true }
  )
}
