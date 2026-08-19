export type NodeStatus = 'connected' | 'connecting' | 'error' | 'disabled'

export type NodeType = {
  id?: number | null
  name: string
  address: string
  port: number
  api_port: number
  xray_version?: string | null
  status?: NodeStatus | null
  message?: string | null
  add_as_new_host?: boolean
  usage_coefficient: number
}

export function defaultNode(): NodeType {
  return {
    name: '',
    address: '',
    port: 62050,
    api_port: 62051,
    xray_version: '',
    usage_coefficient: 1,
    add_as_new_host: true
  }
}

export const NODE_STATUS_TAG: Record<NodeStatus, 'success' | 'info' | 'warning' | 'danger'> = {
  connected: 'success',
  connecting: 'warning',
  error: 'danger',
  disabled: 'info'
}

export type NodeUsageEntry = {
  node_id: number | null
  node_name: string
  uplink: number
  downlink: number
}
export type NodesUsageResponse = { usages: NodeUsageEntry[] }
