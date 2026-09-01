export type PlanFilter = 'all' | 'period' | 'traffic'
export type PlanCategory = 'period' | 'traffic'

export function formatPrice(amount: number): string {
  return amount.toFixed(2)
}

export function currencySymbol(currency: string): string {
  return currency === 'USD' ? '$' : `${currency} `
}

export function pickLocale<T>(locale: string, zh: T, en: T): T {
  return locale.toLowerCase().startsWith('zh') ? zh : en
}
