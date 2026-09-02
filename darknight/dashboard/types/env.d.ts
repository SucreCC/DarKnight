/// <reference types="vite/client" />

declare module '*.vue' {
  import { DefineComponent } from 'vue'
  // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/ban-types
  const component: DefineComponent<{}, {}, any>
  export default component
}

interface ImportMetaEnv {
  readonly VITE_APP_TITLE: string
  readonly VITE_PORT: string
  readonly VITE_OPEN: string
  readonly VITE_BASE_PATH: string
  readonly VITE_OUT_DIR: string
  readonly VITE_BASE_URL: string
  readonly VITE_API_URL: string
  readonly VITE_API_PROXY_TARGET: string
  readonly VITE_SITE_URL: string
  readonly VITE_DROP_DEBUGGER: string
  readonly VITE_DROP_CONSOLE: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
