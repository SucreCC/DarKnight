import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'

dayjs.extend(relativeTime)

export function relativeExpiry(expire: number | null): string | null {
  if (!expire) return null
  return dayjs.unix(expire).fromNow(true)
}

export function isExpired(expire: number | null): boolean {
  if (!expire) return false
  return dayjs.unix(expire).isBefore(dayjs())
}

export function formatDateTime(value: string | number | null): string {
  if (!value) return '-'
  return dayjs(value).format('YYYY-MM-DD HH:mm')
}

export { dayjs }
