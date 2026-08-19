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
}
