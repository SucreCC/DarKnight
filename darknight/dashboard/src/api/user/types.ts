export type UserStatus =
  'active' | 'disabled' | 'limited' | 'expired' | 'on_hold' | 'error' | 'connecting' | 'connected'

export type ProxyKey = 'vmess' | 'vless' | 'trojan' | 'shadowsocks'
export type ProxyKeys = ProxyKey[]

export type ProxyType = {
  vmess?: { id?: string }
  vless?: { id?: string; flow?: string }
  trojan?: { password?: string }
  shadowsocks?: { password?: string; method?: string }
}

export type DataLimitResetStrategy = 'no_reset' | 'day' | 'week' | 'month' | 'year'

export type UserInbounds = Record<string, string[]>

export type User = {
  proxies: ProxyType
  expire: number | null
  data_limit: number | null
  data_limit_reset_strategy: DataLimitResetStrategy
  on_hold_expire_duration: number | null
  lifetime_used_traffic: number
  username: string
  used_traffic: number
  status: UserStatus
  links: string[]
  subscription_url: string
  inbounds: UserInbounds
  note: string
  online_at: string | null
}

export type UserCreate = Pick<
  User,
  | 'inbounds'
  | 'proxies'
  | 'expire'
  | 'data_limit'
  | 'data_limit_reset_strategy'
  | 'on_hold_expire_duration'
  | 'username'
  | 'status'
  | 'note'
>

export type UsersResponse = {
  users: User[]
  total: number
}

export type UserFilters = {
  search?: string
  limit: number
  offset?: number
  sort: string
  status?: 'active' | 'disabled' | 'limited' | 'expired' | 'on_hold'
}

export type ProtocolType = ProxyKey
export type InboundType = {
  tag: string
  protocol: ProtocolType
  network: string
  tls: string
  port?: number
}
export type Inbounds = Record<string, InboundType[]>

export type UsageEntry = { username: string; used_traffic: number }
export type UserUsageResponse = { usages: UsageEntry[]; username: string }

export const RESET_STRATEGIES: {
  title: string
  value: DataLimitResetStrategy
}[] = [
  { title: 'resetStrategyNo', value: 'no_reset' },
  { title: 'resetStrategyDaily', value: 'day' },
  { title: 'resetStrategyWeekly', value: 'week' },
  { title: 'resetStrategyMonthly', value: 'month' },
  { title: 'resetStrategyAnnually', value: 'year' }
]

export const STATUS_TAG_TYPE: Record<
  UserStatus,
  'success' | 'info' | 'warning' | 'danger' | 'primary'
> = {
  active: 'success',
  connected: 'success',
  disabled: 'info',
  expired: 'warning',
  on_hold: 'primary',
  connecting: 'warning',
  limited: 'danger',
  error: 'danger'
}
