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

/** 按 30 天为 1 个月估算周期月数（展示用）。 */
export function billingMonths(durationDays: number): number {
  if (durationDays <= 31) return 1
  if (durationDays <= 100) return 3
  if (durationDays <= 190) return 6
  return 12
}

export function monthlyEquivalent(price: number, durationDays: number): number {
  const months = billingMonths(durationDays)
  return price / months
}

export function discountPercent(
  price: number,
  durationDays: number,
  anchorMonthly: number
): number {
  const months = billingMonths(durationDays)
  const full = anchorMonthly * months
  if (full <= 0 || months <= 1) return 0
  return Math.max(0, Math.round((1 - price / full) * 100))
}

/** 固定折扣：季付 3%；半年 8%；年付 22%。 */
export function planDiscountByMonths(months: number): number {
  if (months <= 1) return 0
  if (months <= 3) return 3
  if (months <= 6) return 8
  return 22
}

export function discountedTotal(anchorMonthly: number, months: number): number {
  const rate = 1 - planDiscountByMonths(months) / 100
  return Math.round(anchorMonthly * months * rate * 100) / 100
}
