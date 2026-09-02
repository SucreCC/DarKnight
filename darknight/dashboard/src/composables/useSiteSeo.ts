import { watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { usePageSeo } from '@/composables/usePageSeo'

export function useSiteSeo(): void {
  const { locale } = useI18n()

  usePageSeo({
    titleKey: 'site.seo.title',
    descriptionKey: 'site.seo.description',
    keywordsKey: 'site.seo.keywords',
    withHreflang: true,
    withFaqSchema: true
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
