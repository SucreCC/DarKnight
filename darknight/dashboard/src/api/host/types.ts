export type HostSecurity = 'inbound_default' | 'none' | 'tls'

export type HostEntry = {
  remark: string
  address: string
  port: number | null
  path: string | null
  sni: string | null
  host: string | null
  security: HostSecurity | string
  alpn: string
  fingerprint: string
  allowinsecure: boolean
  is_disabled: boolean
  mux_enable: boolean
  fragment_setting: string | null
  noise_setting: string | null
  random_user_agent: boolean
  use_sni_as_host: boolean
}

export type HostsSchema = Record<string, HostEntry[]>

export function defaultHost(): HostEntry {
  return {
    remark: '',
    address: '',
    port: null,
    path: '',
    sni: '',
    host: '',
    security: 'inbound_default',
    alpn: '',
    fingerprint: '',
    allowinsecure: false,
    is_disabled: false,
    mux_enable: false,
    fragment_setting: '',
    noise_setting: '',
    random_user_agent: false,
    use_sni_as_host: false
  }
}

export const HOST_SECURITY_OPTIONS: { title: string; value: HostSecurity }[] = [
  { title: "Inbound's default", value: 'inbound_default' },
  { title: 'TLS', value: 'tls' },
  { title: 'None', value: 'none' }
]

export const ALPN_OPTIONS = ['', 'h3', 'h2', 'http/1.1', 'h3,h2,http/1.1', 'h3,h2', 'h2,http/1.1']

export const FINGERPRINT_OPTIONS = [
  '',
  'chrome',
  'firefox',
  'safari',
  'ios',
  'android',
  'edge',
  '360',
  'qq',
  'random',
  'randomized'
]
