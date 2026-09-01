export interface ProductCycle {
  id: number
  cycle_key: string
  label_zh: string
  label_en: string
  price: number
  data_limit_gb: number
  duration_days: number
  is_listed: boolean
  sort_order: number
}

export type ProductCategory = 'period' | 'traffic'

export interface Product {
  id: number
  slug: string
  name_zh: string
  name_en: string
  category: ProductCategory
  features_zh: string[]
  features_en: string[]
  display_cycle_key: string
  sort_order: number
  is_listed: boolean
  created_at: string
  updated_at: string
  cycles: ProductCycle[]
}

export type ProductCycleInput = Omit<ProductCycle, 'id'>

export type ProductCreateBody = {
  slug: string
  name_zh: string
  name_en: string
  features_zh: string[]
  features_en: string[]
  display_cycle_key?: string
  cycles: ProductCycleInput[]
}

export type ProductModifyBody = Partial<
  Omit<Product, 'id' | 'created_at' | 'updated_at' | 'cycles'>
>
