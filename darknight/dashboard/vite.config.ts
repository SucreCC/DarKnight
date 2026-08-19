import { resolve } from 'path'
import type { ConfigEnv, UserConfig } from 'vite'
import { loadEnv } from 'vite'
import { createVitePlugins } from './build/vite'
import { exclude, include } from './build/vite/optimize'

// 当前执行 node 命令时文件夹的地址（工作目录）
const root = process.cwd()

// 路径查找
function pathResolve(dir: string) {
  return resolve(root, '.', dir)
}

// https://vitejs.dev/config/
export default ({ mode }: ConfigEnv): UserConfig => {
  const env = loadEnv(mode, root)
  const proxyTarget = env.VITE_API_PROXY_TARGET || 'http://127.0.0.1:33100'

  return {
    base: env.VITE_BASE_PATH,
    root,
    server: {
      port: Number(env.VITE_PORT) || 3000,
      host: '0.0.0.0',
      open: env.VITE_OPEN === 'true',
      proxy: {
        '/api/v1': { target: proxyTarget, changeOrigin: true }
      }
    },
    publicDir: 'public',
    plugins: createVitePlugins(),
    css: {
      preprocessorOptions: {
        scss: {
          api: 'modern-compiler'
        }
      }
    },
    resolve: {
      extensions: ['.mjs', '.js', '.ts', '.json', '.scss', '.css'],
      alias: [{ find: /\@\//, replacement: `${pathResolve('src')}/` }]
    },
    build: {
      chunkSizeWarningLimit: 2000,
      outDir: env.VITE_OUT_DIR || 'dist',
      reportCompressedSize: false,
      sourcemap: false
    },
    optimizeDeps: { include, exclude }
  }
}
