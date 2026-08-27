/**
 * PayPal CardFields 渲染在 iframe 内，Tailwind 无法穿透，
 * 字体与颜色只能在初始化时以具体色值传入。这里读的是 globals.css 中
 * 专为此用途定义的十六进制变量（iframe 内不保证支持 oklch）。
 */
export function readPayPalFieldStyle(): Record<string, Record<string, string>> {
  const css = getComputedStyle(document.documentElement)
  const read = (name: string, fallback: string) => css.getPropertyValue(name).trim() || fallback

  const color = read('--paypal-field-color', '#18181b')
  const placeholder = read('--paypal-field-placeholder', '#a1a1aa')
  const focus = read('--paypal-field-focus', '#6366f1')
  const invalid = read('--paypal-field-invalid', '#ef4444')

  return {
    input: {
      color,
      'font-size': '14px',
      'font-family':
        "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
      padding: '0'
    },
    '::placeholder': { color: placeholder },
    ':focus': { color: focus },
    '.invalid': { color: invalid }
  }
}
