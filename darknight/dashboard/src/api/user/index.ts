import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import type { MaybeRefOrGetter } from 'vue'
import { toValue } from 'vue'
import { http } from '@/config/axios'
import type {
  Inbounds,
  User,
  UserCreate,
  UserFilters,
  UsersResponse,
  UserUsageResponse
} from './types'

export const usersQueryKey = ['users'] as const
export const inboundsQueryKey = ['inbounds'] as const
export const systemQueryKey = ['system'] as const

function cleanFilters(filters: UserFilters): Record<string, unknown> {
  const query: Record<string, unknown> = {}
  ;(Object.keys(filters) as (keyof UserFilters)[]).forEach((key) => {
    const value = filters[key]
    if (value !== undefined && value !== null && value !== '') {
      query[key] = value
    }
  })
  return query
}

export function useUsersQuery(filters: MaybeRefOrGetter<UserFilters>) {
  return useQuery({
    queryKey: [...usersQueryKey, filters],
    queryFn: () => http<UsersResponse>('/users', { query: cleanFilters(toValue(filters)) }),
    placeholderData: (prev) => prev
  })
}

export function useInboundsQuery() {
  return useQuery({
    queryKey: inboundsQueryKey,
    queryFn: () => http<Inbounds>('/inbounds'),
    staleTime: 5 * 60 * 1000
  })
}

export function useUserMutations() {
  const queryClient = useQueryClient()
  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: usersQueryKey })
    queryClient.invalidateQueries({ queryKey: systemQueryKey })
  }

  const createUser = useMutation({
    mutationFn: (body: UserCreate) => http<User>('/user', { method: 'POST', body }),
    onSuccess: invalidate
  })

  const updateUser = useMutation({
    mutationFn: (body: UserCreate) => http<User>(`/user/${body.username}`, { method: 'PUT', body }),
    onSuccess: invalidate
  })

  const deleteUser = useMutation({
    mutationFn: (username: string) => http(`/user/${username}`, { method: 'DELETE' }),
    onSuccess: invalidate
  })

  const resetUserUsage = useMutation({
    mutationFn: (username: string) => http(`/user/${username}/reset`, { method: 'POST' }),
    onSuccess: invalidate
  })

  const resetAllUsage = useMutation({
    mutationFn: () => http('/users/reset', { method: 'POST' }),
    onSuccess: invalidate
  })

  const revokeSub = useMutation({
    mutationFn: (username: string) =>
      http<User>(`/user/${username}/revoke_sub`, { method: 'POST' }),
    onSuccess: invalidate
  })

  return {
    createUser,
    updateUser,
    deleteUser,
    resetUserUsage,
    resetAllUsage,
    revokeSub
  }
}

export function fetchUserUsage(username: string, query: { start?: string; end?: string }) {
  return http<UserUsageResponse>(`/user/${username}/usage`, {
    method: 'GET',
    query
  })
}
