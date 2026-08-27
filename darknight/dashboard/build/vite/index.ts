import Vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

export function createVitePlugins() {
  const plugins = [
    Vue(),
    tailwindcss(),
    AutoImport({
      include: [
        /\.[tj]sx?$/, // .ts, .tsx, .js, .jsx
        /\.vue$/,
        /\.vue\?vue/ // .vue
      ],
      imports: ['vue', 'vue-router', 'vue-i18n', 'pinia', '@vueuse/core'],
      resolvers: [ElementPlusResolver({ importStyle: false })],
      dts: 'types/auto-imports.d.ts',
      eslintrc: {
        enabled: true,
        filepath: './.eslintrc-auto-import.json',
        globalsPropValue: true
      }
    }),
    Components({
      dts: 'types/auto-components.d.ts',
      resolvers: [ElementPlusResolver({ importStyle: false })],
      // shadcn-vue 组件走显式 import，不能再被全局注册一次。
      globs: ['src/components/**/*.vue', '!src/components/ui/**']
    })
  ]

  return plugins.filter(Boolean)
}
