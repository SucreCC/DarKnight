import Vue from '@vitejs/plugin-vue'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

export function createVitePlugins() {
  const plugins = [
    Vue(),
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
      globs: ['src/components/**/*.vue']
    })
  ]

  return plugins.filter(Boolean)
}
