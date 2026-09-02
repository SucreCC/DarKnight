import { useQuery } from '@tanstack/vue-query'
import { fetchPortalMe } from '@/api/portal'

export function usePortalMe() {
  return useQuery({
    queryKey: ['portal', 'me'],
    queryFn: fetchPortalMe,
    refetchOnWindowFocus: false
  })
}
