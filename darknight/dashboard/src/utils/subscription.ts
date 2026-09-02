/** 将相对订阅路径转为可扫码/分享的完整 URL */
export function absoluteSubscriptionUrl(url: string): string {
  if (!url) return ''
  return url.startsWith('/') ? `${window.location.origin}${url}` : url
}
