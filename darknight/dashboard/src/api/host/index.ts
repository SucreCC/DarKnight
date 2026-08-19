import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { http } from '@/config/axios'
import type { HostsSchema } from './types'

export const hostsQueryKey = ['hosts'] as const

export function useHostsQuery() {
  return useQuery({
    queryKey: hostsQueryKey,
    queryFn: () => http<HostsSchema>('/hosts'),
    refetchOnWindowFocus: false
  })
}

export function useSaveHosts() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (body: HostsSchema) => http<HostsSchema>('/hosts', { method: 'PUT', body }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: hostsQueryKey })
  })
}
