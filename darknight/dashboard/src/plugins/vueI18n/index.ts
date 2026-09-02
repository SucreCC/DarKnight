import { createI18n } from 'vue-i18n'
import type { Router } from 'vue-router'
import en from '@/locales/en.json'
import zh from '@/locales/zh.json'
import ruBase from '@/locales/ru.json'
import faBase from '@/locales/fa.json'
import portalRu from '@/locales/portal.ru.json'
import portalFa from '@/locales/portal.fa.json'
import siteRu from '@/locales/site.ru.json'
import siteFa from '@/locales/site.fa.json'

const ru = { ...ruBase, ...portalRu, ...siteRu }
const fa = { ...faBase, ...portalFa, ...siteFa }

const LANG_KEY = 'darknight-lang'

export const SUPPORTED_LOCALES = [
  { value: 'en', label: 'English' },
  { value: 'zh', label: '中文' },
  { value: 'ru', label: 'Русский' },
  { value: 'fa', label: 'فارسی' }
] as const

export type LocaleCode = (typeof SUPPORTED_LOCALES)[number]['value']

function detectLocale(): LocaleCode {
  const saved = localStorage.getItem(LANG_KEY) as LocaleCode | null
  if (saved && SUPPORTED_LOCALES.some((l) => l.value === saved)) return saved
  const nav = navigator.language.split('-')[0]
  if (SUPPORTED_LOCALES.some((l) => l.value === nav)) return nav as LocaleCode
  return 'en'
}

export const i18n = createI18n({
  legacy: false,
  locale: detectLocale(),
  fallbackLocale: 'en',
  // Flat locale keys + emails with "@" must not be parsed as linked messages.
  messageResolver: (obj, path) => {
    const msg = (obj as Record<string, unknown>)[path]
    if (typeof msg !== 'string') return null
    return msg.includes('@') ? msg.replaceAll('@', "{'@'}") : msg
  },
  messages: { en, zh, ru, fa }
})

export function setLocale(locale: LocaleCode): void {
  i18n.global.locale.value = locale
  localStorage.setItem(LANG_KEY, locale)
  document.documentElement.setAttribute('lang', locale === 'zh' ? 'zh-CN' : locale)
  document.documentElement.setAttribute('dir', locale === 'fa' ? 'rtl' : 'ltr')
}

function parseLocaleQuery(value: unknown): LocaleCode | null {
  if (typeof value !== 'string') return null
  return SUPPORTED_LOCALES.some((item) => item.value === value) ? (value as LocaleCode) : null
}

export function applyLocaleFromQuery(router: Router): void {
  const sync = (queryLang: unknown) => {
    const locale = parseLocaleQuery(queryLang)
    if (locale) setLocale(locale)
  }

  sync(router.currentRoute.value.query.lang)
  router.afterEach((to) => sync(to.query.lang))
}
