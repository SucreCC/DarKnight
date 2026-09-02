export interface Product {
  id: number
  slug: string
  name_zh: string
  name_en: string
  category: 'period' | 'traffic'
  features_zh: string[]
  features_en: string[]
  price: number
  duration_days: number
  sort_order: number
  is_listed: boolean
  created_at: string
  updated_at: string
}

export type ProductCreateBody = {
  slug: string
  name_zh: string
  name_en: string
  features_zh: string[]
  features_en: string[]
  price: number
  duration_days: number
  is_listed?: boolean
}

export type ProductModifyBody = Partial<
  Omit<Product, 'id' | 'created_at' | 'updated_at'>
>
