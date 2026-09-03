import type { LocaleCode } from '@/plugins/vueI18n'

export const SITE_URL = (import.meta.env.VITE_SITE_URL || 'https://darkight.com').replace(/\/$/, '')

export const SITE_NAME = 'DarKnight'

export const LOCALE_HREFLANG: Record<LocaleCode, string> = {
  en: 'en',
  zh: 'zh-CN',
  ru: 'ru',
  fa: 'fa'
}

export const PUBLIC_SITEMAP_PATHS = [
  '/',
  '/pricing',
  '/guides',
  '/faq',
  '/blog',
  '/privacy',
  '/terms'
] as const

export function buildCanonicalUrl(path: string, locale: LocaleCode): string {
  const normalized = path === '/' ? '' : path
  const langQuery = locale !== 'en' ? `?lang=${locale}` : ''
  return `${SITE_URL}${normalized}${langQuery}`
}

export function buildAlternateUrls(path: string): { hreflang: string; href: string }[] {
  const normalized = path === '/' ? '' : path
  return (Object.entries(LOCALE_HREFLANG) as [LocaleCode, string][]).map(([locale, hreflang]) => ({
    hreflang,
    href:
      locale === 'en'
        ? `${SITE_URL}${normalized}`
        : `${SITE_URL}${normalized}?lang=${locale}`
  }))
}
