import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import type { Ref } from 'vue'
import { http } from '@/config/axios'
import type { NodesUsageResponse, NodeType } from './types'

export const nodesQueryKey = ['nodes'] as const

export function useNodesQuery(refetchInterval?: Ref<number | undefined>) {
  return useQuery({
    queryKey: nodesQueryKey,
    queryFn: () => http<NodeType[]>('/nodes'),
    refetchInterval: () => refetchInterval?.value,
    refetchOnWindowFocus: false
  })
}

export function useNodeMutations() {
  const queryClient = useQueryClient()
  const invalidate = () => queryClient.invalidateQueries({ queryKey: nodesQueryKey })

  const addNode = useMutation({
    mutationFn: (body: NodeType) => http<NodeType>('/node', { method: 'POST', body }),
    onSuccess: invalidate
  })

  const updateNode = useMutation({
    mutationFn: (body: NodeType) => http<NodeType>(`/node/${body.id}`, { method: 'PUT', body }),
    onSuccess: invalidate
  })

  const deleteNode = useMutation({
    mutationFn: (id: number) => http(`/node/${id}`, { method: 'DELETE' }),
    onSuccess: invalidate
  })

  const reconnectNode = useMutation({
    mutationFn: (id: number) => http(`/node/${id}/reconnect`, { method: 'POST' }),
    onSuccess: invalidate
  })

  return { addNode, updateNode, deleteNode, reconnectNode }
}

export function fetchNodesUsage(query: { start?: string; end?: string }) {
  return http<NodesUsageResponse>('/nodes/usage', { query })
}
