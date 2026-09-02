export type LoginAccess = 'user' | 'admin' | 'sudo'

export interface LoginToken {
  access_token: string
  token_type?: string
  access: LoginAccess
}

export interface PortalUser {
  username: string
  email: string
  status: string
  used_traffic: number
  data_limit: number | null
  expire: number | null
  subscription_url: string
  links: string[]
  created_at: string
  plan_id?: string | null
  plan_name_zh?: string | null
  plan_name_en?: string | null
}
