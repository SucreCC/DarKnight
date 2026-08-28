/**
 * PayPal CardFields 渲染在 iframe 内，Tailwind 无法穿透。
 * 所有可见样式只画在 iframe 内的 input 上，避免与外层容器套娃。
 */
function readTokens() {
  const css = getComputedStyle(document.documentElement)
  const read = (name: string, fallback: string) => css.getPropertyValue(name).trim() || fallback
  return {
    color: read('--paypal-field-color', '#18181b'),
    placeholder: read('--paypal-field-placeholder', '#a1a1aa'),
    focus: read('--paypal-field-focus', '#6366f1'),
    invalid: read('--paypal-field-invalid', '#ef4444'),
    bg: read('--paypal-field-bg', '#f4f4f5'),
    focusRing: read('--paypal-field-focus-ring', 'rgba(99, 102, 241, 0.3)')
  }
}

const FONT =
  "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"

function baseInput(color: string, bg: string, padding: string) {
  return {
    color,
    background: bg,
    border: 'none',
    outline: 'none',
    padding,
    margin: '0',
    'box-shadow': 'none',
    'border-radius': '6px',
    'font-size': '14px',
    'line-height': '20px',
    'font-family': FONT
  }
}

function pack(
  input: Record<string, string>,
  placeholder: string,
  focus: string,
  focusRing: string,
  invalid: string
) {
  return {
    input,
    '::placeholder': { color: placeholder },
    ':focus': {
      ...input,
      color: focus,
      'box-shadow': `0 0 0 3px ${focusRing}`
    },
    '.invalid': { ...input, color: invalid }
  }
}

export function readPayPalFieldStyle(): Record<string, Record<string, string>> {
  const { color, placeholder, focus, invalid, bg, focusRing } = readTokens()
  return pack(baseInput(color, bg, '11px 12px'), placeholder, focus, focusRing, invalid)
}

export function readPayPalNumberFieldStyle(): Record<string, Record<string, string>> {
  const { color, placeholder, focus, invalid, bg, focusRing } = readTokens()
  return pack(baseInput(color, bg, '11px 12px 11px 42px'), placeholder, focus, focusRing, invalid)
}
