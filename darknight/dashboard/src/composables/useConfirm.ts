import { reactive } from 'vue'
import { i18n } from '@/plugins/vueI18n'

export interface ConfirmOptions {
  title: string
  description: string
  confirmText?: string
  cancelText?: string
  destructive?: boolean
}

interface ConfirmState {
  open: boolean
  options: Required<Omit<ConfirmOptions, 'destructive'>> & { destructive: boolean }
}

export const confirmState = reactive<ConfirmState>({
  open: false,
  options: { title: '', description: '', confirmText: '', cancelText: '', destructive: false }
})

let pending: { resolve: () => void; reject: () => void } | null = null

/** 关闭对话框并结算 Promise。取消走 reject，保留调用点 try/catch 的写法。 */
export function resolveConfirm(confirmed: boolean): void {
  confirmState.open = false
  const current = pending
  pending = null
  if (!current) return
  if (confirmed) current.resolve()
  else current.reject()
}

export function useConfirm() {
  function confirm(options: ConfirmOptions): Promise<void> {
    // 同一时刻只允许一个确认框；新的请求先把旧的当作取消结算掉。
    if (pending) resolveConfirm(false)

    const t = i18n.global.t
    confirmState.options = {
      title: options.title,
      description: options.description,
      confirmText: options.confirmText ?? t('confirm'),
      cancelText: options.cancelText ?? t('cancel'),
      destructive: options.destructive ?? false
    }
    confirmState.open = true

    return new Promise<void>((resolve, reject) => {
      pending = { resolve, reject }
    })
  }

  return { confirm }
}
