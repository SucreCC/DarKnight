import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { http } from '@/config/axios'
import type { Product, ProductCreateBody, ProductModifyBody } from './types'

export const productsQueryKey = ['products'] as const

export function useProductsQuery() {
  return useQuery({
    queryKey: productsQueryKey,
    queryFn: () => http<Product[]>('/products'),
    refetchOnWindowFocus: false
  })
}

export function useProductMutations() {
  const queryClient = useQueryClient()
  const invalidate = () => queryClient.invalidateQueries({ queryKey: productsQueryKey })

  const addProduct = useMutation({
    mutationFn: (body: ProductCreateBody) => http<Product>('/product', { method: 'POST', body }),
    onSuccess: invalidate
  })

  const updateProduct = useMutation({
    mutationFn: ({ id, body }: { id: number; body: ProductModifyBody }) =>
      http<Product>(`/product/${id}`, { method: 'PUT', body }),
    onSuccess: invalidate
  })

  const deleteProduct = useMutation({
    mutationFn: (id: number) => http(`/product/${id}`, { method: 'DELETE' }),
    onSuccess: invalidate
  })

  return { addProduct, updateProduct, deleteProduct }
}
