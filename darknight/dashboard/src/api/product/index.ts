import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { http } from '@/config/axios'
import type { Product, ProductCreateBody, ProductCycleInput, ProductModifyBody } from './types'

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

  const addCycle = useMutation({
    mutationFn: ({ productId, body }: { productId: number; body: ProductCycleInput }) =>
      http(`/product/${productId}/cycle`, { method: 'POST', body }),
    onSuccess: invalidate
  })

  const updateCycle = useMutation({
    mutationFn: ({
      productId,
      cycleId,
      body
    }: {
      productId: number
      cycleId: number
      body: Partial<ProductCycleInput>
    }) => http(`/product/${productId}/cycle/${cycleId}`, { method: 'PUT', body }),
    onSuccess: invalidate
  })

  const deleteCycle = useMutation({
    mutationFn: ({ productId, cycleId }: { productId: number; cycleId: number }) =>
      http(`/product/${productId}/cycle/${cycleId}`, { method: 'DELETE' }),
    onSuccess: invalidate
  })

  return { addProduct, updateProduct, deleteProduct, addCycle, updateCycle, deleteCycle }
}
