import axios from 'axios'
import type { AxiosInstance, AxiosRequestConfig } from 'axios'
import { formatToken, getAccessToken, removeToken } from '@/utils/auth'

const DEFAULT_API_BASE = '/api/v1'

/**
 * 接口根地址。
 *
 * 生产构建时由后端注入 VITE_BASE_URL + VITE_API_URL（见 darknight/dashboard/__init__.py
 * 的 split_api_base）；开发环境两者均为空，回落到由 vite 代理转发的 /api/v1。
 */
export function getApiBase(): string {
  const joined = `${import.meta.env.VITE_BASE_URL ?? ''}${import.meta.env.VITE_API_URL ?? ''}`
  return (joined || DEFAULT_API_BASE).replace(/\/+$/, '')
}

const instance: AxiosInstance = axios.create({
  baseURL: getApiBase(),
  timeout: 30000
})

instance.interceptors.request.use((config) => {
  const token = getAccessToken()
  if (token) {
    config.headers.Authorization = formatToken(token)
  }
  return config
})

instance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error?.response?.status === 401) {
      removeToken()
      if (!window.location.hash.startsWith('#/login')) {
        window.location.hash = '#/login'
      }
    }
    return Promise.reject(error)
  }
)

/** 保持与原 ofetch 封装一致的调用签名，调用方无需改动。 */
export interface HttpOptions extends Omit<AxiosRequestConfig, 'url' | 'data' | 'params'> {
  body?: unknown
  query?: Record<string, unknown>
}

export function http<T = unknown>(url: string, options: HttpOptions = {}): Promise<T> {
  const { body, query, ...rest } = options
  return instance.request<T>({ url, data: body, params: query, ...rest }).then((res) => res.data)
}

/**
 * 取出 FastAPI 错误响应里的 detail 原值（可能是字符串，也可能是字段名到错误的对象）。
 * 只负责定位，格式化交给调用方，各页面的展示口径保持原样。
 */
export function extractErrorDetail(err: unknown): unknown {
  return (err as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail
}

export default instance
