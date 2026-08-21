# 前端架构对齐 yudao-ui-admin-vue3 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 `darknight/dashboard/` 的工程骨架、目录约定与封装体系完全对齐 yudao-ui-admin-vue3，业务功能保持等价。

**Architecture:** 原地重建——在现有目录内按 yudao 规范重排结构，从本地参考仓库 `e:\kai\yudao-ref` 逐块移植基础设施代码，再把 5 个业务模块改写成 `views/` + `api/` 形态。构建产物从 `build/` 改为 `dist/`，静态资源目录从 `statics` 改为 Vite 默认的 `assets`，Python 侧同步适配。

**Tech Stack:** Vue 3.5 + TypeScript 5.7 + Vite 6 + Element Plus 2.9 + Pinia 2 + vue-router 4 + vue-i18n 10 + axios + UnoCSS + SCSS + ESLint 9 + Stylelint

**Spec:** `docs/superpowers/specs/2026-08-19-yudao-admin-alignment-design.md`

**参考仓库:** `e:\kai\yudao-ref`（已 clone，只读，禁止修改）

## Global Constraints

- 前端必须留在 `darknight/dashboard/`，不得移动目录。
- 路由必须用 `createWebHashHistory()`。产物由 FastAPI `StaticFiles(html=True)` 挂载在 `/dashboard/`，history 模式刷新子路径会 404。
- `npm run build` 必须在无额外命令行参数的情况下产出正确结构（后端直接调用它）。
- `VITE_BASE_URL` 与 `VITE_API_URL` 由 Python 在构建时通过进程环境变量注入，**不得写入任何 `.env` 文件**，否则会覆盖注入值。
- `VITE_BASE_PATH` 必须是 `./`——产物挂在 `/dashboard/` 子路径下，绝对路径会 404。
- dev 环境保留 `/api/v1` → `http://127.0.0.1:33100` 代理，目标可由 `VITE_API_PROXY_TARGET` 覆盖。
- 样式用 **SCSS**（yudao 用的就是 SCSS），不要改成 Less。
- 业务页面**不使用** `useTable` / `useCrudSchemas` / `Search` 组件，一律跟随 yudao 的实际页面模板 `e:\kai\yudao-ref\src\views\system\post\index.vue` 的手写模式。
- 不引入：字典体系、租户、验证码、接口加解密、formCreate、刷新 token、社交登录、wangEditor、mock、husky / lint-staged / commitlint、测试框架。
- 不新增业务功能：不补 Hosts 高级字段（sockopt / fragment / noise），不补节点用量 echarts 图表。
- 不做 RTL 镜像布局；四语言翻译全部保留，界面方向统一 LTR。
- **本次不使用 git**：不建分支、不提交、不 stash。任务之间没有回滚点。
- 环境为 Windows PowerShell。用 `Copy-Item -Recurse`、`Remove-Item -Recurse -Force`，不要用 bash 的 `cp -r` / `rm -rf` 语法。

## 执行期决策记录

执行过程中发现的、与原计划文本不符的事实，以本节为准：

| # | 决策 | 原因 | 影响任务 |
| --- | --- | --- | --- |
| D1 | **不使用 svg sprite 方案**：不装 `vite-plugin-svg-icons`，不移植 `src/plugins/svgIcon`，不保留 `types/svg-icons-register.d.ts`，`main.ts` 不 import `virtual:svg-icons-register`。图标一律走 iconify（`@iconify/vue` + `@iconify/json` 离线图标集），路由 `meta.icon` 用 `ep:xxx` 形式 | 本项目没有任何本地 svg 资源；`vite-plugin-svg-icons` 是 2022 年的包且传递依赖大量 deprecated；yudao 自己用的也不是 `@iconify/iconify`（该包已停止维护） | 2、4、8、10 |
| D2 | `pinia-plugin-persistedstate` 用 **v3.2.3** 而非 yudao 的 v4 | v4 的 peer 要求 `pinia >= 3`，与本项目 Pinia 2 真实 ERESOLVE 冲突 | 7 |
| D3 | 选择性持久化用 v3 的 **`paths`** 选项，不是 v4 的 `pick` / `omit` | 同 D2 | 7 |
| D4 | stylelint 用 `stylelint-config-standard-scss` + `stylelint-config-recommended-vue`，yudao 的配置文件 extends 的是 `stylelint-config-standard` / `-recommended`，复制后**必须改 extends 名** | 本项目用 SCSS，需要 scss 方言支持 | 3 |

---

## Task 1: 依赖调整

**Files:**
- Modify: `darknight/dashboard/package.json`

**Interfaces:**
- Produces: 后续任务可用的依赖集与 npm scripts。

- [ ] **Step 1: 对照参考仓库确认版本**

读 `e:\kai\yudao-ref\package.json`，记录以下包在 yudao 中的版本：`axios`、`qs`、`web-storage-cache`、`unocss`、`@iconify/iconify`、`nprogress`、`vue-types`、`lodash-es`、`mitt`、`animate.css`、`pinia-plugin-persistedstate`。安装时用相同的大版本，避免 API 不一致。

- [ ] **Step 2: 卸载被替换的依赖**

```powershell
cd e:\kai\DarKnight\darknight\dashboard
npm uninstall '@tanstack/vue-query' ofetch zod
```

`sass` **保留**（继续用 SCSS）。

- [ ] **Step 3: 安装运行时依赖**

```powershell
npm install axios qs web-storage-cache nprogress vue-types lodash-es mitt animate.css '@iconify/iconify' pinia-plugin-persistedstate
```

- [ ] **Step 4: 安装开发依赖**

```powershell
npm install -D unocss '@unocss/preset-uno' '@unocss/preset-attributify' '@unocss/transformer-variant-group' '@iconify/json' '@types/nprogress' '@types/lodash-es' '@types/qs' '@vitejs/plugin-vue-jsx' vite-plugin-svg-icons autoprefixer postcss eslint '@eslint/js' typescript-eslint eslint-plugin-vue vue-eslint-parser eslint-config-prettier eslint-plugin-prettier prettier stylelint stylelint-config-standard-scss stylelint-config-recommended-vue stylelint-config-html stylelint-order postcss-html
```

- [ ] **Step 5: 改写 scripts**

`package.json` 的 `scripts` 整块替换为：

```json
{
  "scripts": {
    "dev": "vite --mode local",
    "build": "vite build --mode prod",
    "build:local": "vite build --mode local",
    "preview": "vite preview --port 3000",
    "ts:check": "vue-tsc --noEmit",
    "lint": "npm run lint:eslint:check && npm run lint:style:check && npm run lint:format:check",
    "lint:eslint": "eslint --fix \"src/**/*.{vue,ts,tsx,js}\"",
    "lint:eslint:check": "eslint \"src/**/*.{vue,ts,tsx,js}\"",
    "lint:style": "stylelint --fix \"src/**/*.{vue,css,scss}\"",
    "lint:style:check": "stylelint \"src/**/*.{vue,css,scss}\"",
    "lint:format": "prettier --write \"src/**/*.{vue,ts,tsx,js,json,scss}\"",
    "lint:format:check": "prettier --check \"src/**/*.{vue,ts,tsx,js,json,scss}\""
  }
}
```

`build` 必须无参数可用——后端直接调 `npm run build`，`--mode prod` 是脚本内置的。

- [ ] **Step 6: 验证**

```powershell
npm ls axios unocss web-storage-cache eslint stylelint --depth=0
```

预期：全部列出且无 `UNMET DEPENDENCY`。

---

## Task 2: 构建骨架与产物目录迁移

**Files:**
- Create: `darknight/dashboard/build/vite/index.ts`
- Create: `darknight/dashboard/build/vite/optimize.ts`
- Create: `darknight/dashboard/.env` / `.env.local` / `.env.dev` / `.env.prod`
- Modify: `darknight/dashboard/vite.config.ts`（全量重写）
- Modify: `darknight/dashboard/tsconfig.json`
- Modify: `darknight/dashboard/.gitignore`
- Modify: `darknight/dashboard/example.env`
- Modify: `darknight/dashboard/__init__.py`

**Interfaces:**
- Produces: `createVitePlugins(isBuild: boolean, env: Record<string,string>): PluginOption[]` from `build/vite`；`{ include, exclude }` from `build/vite/optimize`；产物落在 `dist/` + `dist/assets/`。

- [ ] **Step 1: 删除旧产物目录**

```powershell
cd e:\kai\DarKnight\darknight\dashboard
Remove-Item -Recurse -Force build -ErrorAction SilentlyContinue
```

- [ ] **Step 2: 移植 `build/vite/`**

```powershell
New-Item -ItemType Directory -Force -Path build\vite
Copy-Item e:\kai\yudao-ref\build\vite\index.ts build\vite\index.ts
Copy-Item e:\kai\yudao-ref\build\vite\optimize.ts build\vite\optimize.ts
```

改写 `build/vite/index.ts`：保留 `createVitePlugins(isBuild, env)` 的签名与整体结构，
删除 yudao 特有的插件（formCreate、tongji 相关）以及 **`createSvgIconsPlugin`**
（见下方决策记录），保留 vue、vueJsx、UnoCSS、AutoImport、Components。
给 AutoImport 加上 eslintrc 生成：

```ts
AutoImport({
  imports: ['vue', 'vue-router', 'vue-i18n', 'pinia', '@vueuse/core'],
  resolvers: [ElementPlusResolver({ importStyle: false })],
  dts: 'types/auto-imports.d.ts',
  eslintrc: { enabled: true, filepath: './.eslintrc-auto-import.json', globalsPropValue: true }
})
```

改写 `build/vite/optimize.ts` 的 `include` 数组：删掉 yudao 业务依赖（bpmn、formCreate、
crypto 等），只留本项目实际用到的。

- [ ] **Step 3: 重写 `vite.config.ts`**

以 `e:\kai\yudao-ref\vite.config.ts` 为蓝本，做四处适配：加回 dev 代理（yudao 注释掉了）、
`assetsDir` 不设（用默认 `assets`）、`publicDir` 指向 `src/public`、SCSS 注入路径按本项目。

```ts
import { dirname, relative, resolve } from 'path'
import type { ConfigEnv, UserConfig } from 'vite'
import { loadEnv, normalizePath } from 'vite'
import { createVitePlugins } from './build/vite'
import { exclude, include } from './build/vite/optimize'

const root = process.cwd()

function pathResolve(dir: string) {
  return resolve(root, '.', dir)
}

export default ({ command, mode }: ConfigEnv): UserConfig => {
  const isBuild = command === 'build'
  const env = loadEnv(mode, root)
  const proxyTarget = env.VITE_API_PROXY_TARGET || 'http://127.0.0.1:33100'

  return {
    base: env.VITE_BASE_PATH,
    root,
    publicDir: pathResolve('src/public'),
    server: {
      port: Number(env.VITE_PORT) || 3000,
      host: '0.0.0.0',
      open: env.VITE_OPEN === 'true',
      proxy: {
        '/api/v1': { target: proxyTarget, changeOrigin: true }
      }
    },
    plugins: createVitePlugins(isBuild, env),
    css: {
      preprocessorOptions: {
        scss: {
          additionalData: '@use "@/styles/variables.scss" as *;',
          api: 'modern-compiler'
        }
      }
    },
    resolve: {
      extensions: ['.mjs', '.js', '.ts', '.jsx', '.tsx', '.json', '.scss', '.css'],
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
```

- [ ] **Step 4: 创建四个 env 文件**

`.env`（公共，所有模式都加载）：

```
VITE_APP_TITLE=DarKnight
VITE_PORT=3000
VITE_OPEN=false
VITE_BASE_PATH=./
VITE_OUT_DIR=dist
```

`.env.local`（本地开发）：

```
VITE_API_PROXY_TARGET=http://127.0.0.1:33100
```

`.env.dev`：

```
VITE_API_PROXY_TARGET=http://127.0.0.1:33100
```

`.env.prod`（生产构建，后端调用的就是这个 mode）：

```
VITE_DROP_DEBUGGER=true
VITE_DROP_CONSOLE=false
```

**四个文件里都不得出现 `VITE_BASE_URL` 或 `VITE_API_URL`**（Global Constraints）。

- [ ] **Step 5: 更新 `example.env` 与 `.gitignore`**

`example.env`：

```
# VITE_BASE_URL 与 VITE_API_URL 由后端在构建时注入，通常无需手动设置
# VITE_BASE_URL=
# VITE_API_URL=/api/v1
# 开发环境 /api/v1 代理目标
VITE_API_PROXY_TARGET=http://127.0.0.1:33100
```

`.gitignore`：把 `build/` 改成 `dist/`，追加 `.eslintrc-auto-import.json` 与 `types/auto-imports.d.ts`。

- [ ] **Step 6: 更新 `tsconfig.json`**

`include` 加上 `types/**/*.d.ts` 与 `src/types/**/*.d.ts`；`paths` 保持 `"@/*": ["src/*"]`；
`types` 数组含 `vite/client`、`element-plus/global`。

- [ ] **Step 7: 改 `__init__.py`**

```python
from __future__ import annotations

import logging
import os
import subprocess
from pathlib import Path
from urllib.parse import urlsplit

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from darknight.services.config.models import AppConfig

logger = logging.getLogger(__name__)
base_dir = Path(__file__).parent
build_dir = base_dir / "dist"
statics_dir = build_dir / "assets"


def split_api_base(vite_base_api: str) -> tuple[str, str]:
    """Split the configured API base into the origin and path parts.

    The dashboard follows the yudao convention where the axios baseURL is
    composed as VITE_BASE_URL + VITE_API_URL.
    """
    parts = urlsplit(vite_base_api)
    path = parts.path.rstrip("/")
    if parts.scheme and parts.netloc:
        return f"{parts.scheme}://{parts.netloc}", path
    return "", path


def build_dashboard(vite_base_api: str) -> None:
    base_url, api_url = split_api_base(vite_base_api)
    proc = subprocess.Popen(
        ["npm", "run", "build"],
        env={
            **os.environ,
            "VITE_BASE_URL": base_url,
            "VITE_API_URL": api_url,
        },
        cwd=base_dir,
        shell=os.name == "nt",
    )
    if proc.wait() != 0:
        raise RuntimeError("Dashboard build failed")


def register_dashboard(app: FastAPI, app_config: AppConfig) -> None:
    web = app_config.web
    dashboard_path = web.dashboard_path.rstrip("/") + "/"

    if not build_dir.is_dir() or not (build_dir / "index.html").exists():
        logger.info("Building dashboard (first run, may take a minute)...")
        build_dashboard(web.vite_base_api)

    app.mount(
        dashboard_path,
        StaticFiles(directory=build_dir, html=True),
        name="dashboard",
    )
    if statics_dir.is_dir():
        app.mount(
            "/assets/",
            StaticFiles(directory=statics_dir, html=True),
            name="assets",
        )


__all__ = ["register_dashboard", "build_dashboard", "split_api_base"]
```

`darknight/services/config/models/web.py` **不动**。

- [ ] **Step 8: 验证构建产物结构**

此时 `src/` 仍是旧结构。旧代码引用的 `ofetch` 已被卸载，构建会失败——这是预期的。
本步只验证配置本身能被 Vite 解析：

```powershell
npx vite build --mode prod
```

预期：报错来自 `src/` 下的旧业务代码（找不到 `ofetch` / `@tanstack/vue-query`），
**不应**出现 `vite.config.ts`、`build/vite/index.ts`、`.env` 解析类错误。

- [ ] **Step 9: 验证环境变量注入链路**

写一个临时脚本验证 Python 的拆分逻辑：

```powershell
cd e:\kai\DarKnight
python -c "from darknight.dashboard import split_api_base; print(split_api_base('/api/v1/')); print(split_api_base('http://127.0.0.1:33100/api/v1/'))"
```

预期输出：

```
('', '/api/v1')
('http://127.0.0.1:33100', '/api/v1')
```

---

## Task 3: Lint 工具链

**Files:**
- Create: `darknight/dashboard/eslint.config.mjs`
- Create: `darknight/dashboard/stylelint.config.js`
- Create: `darknight/dashboard/prettier.config.js`
- Create: `darknight/dashboard/postcss.config.js`
- Create: `darknight/dashboard/.editorconfig` / `.prettierignore` / `.stylelintignore`
- Delete: `darknight/dashboard/.prettierrc.json`

- [ ] **Step 1: 移植七个配置文件**

```powershell
cd e:\kai\DarKnight\darknight\dashboard
Copy-Item e:\kai\yudao-ref\eslint.config.mjs .
Copy-Item e:\kai\yudao-ref\stylelint.config.js .
Copy-Item e:\kai\yudao-ref\prettier.config.js .
Copy-Item e:\kai\yudao-ref\postcss.config.js .
Copy-Item e:\kai\yudao-ref\.editorconfig .
Copy-Item e:\kai\yudao-ref\.prettierignore .
Copy-Item e:\kai\yudao-ref\.stylelintignore .
Remove-Item .prettierrc.json
```

- [ ] **Step 2: 去掉指向 yudao 业务目录的忽略项**

三个 ignore 文件里凡是提到 `src/views/mall`、`bpmnProcessDesigner`、`SimpleProcessDesignerV2`
之类 yudao 专有路径的行全部删掉。统一保留：`dist`、`node_modules`、`src/public`、
`types/auto-imports.d.ts`、`types/components.d.ts`。

`stylelint.config.js` 的 `extends` 必须改名（决策记录 D4）：
`stylelint-config-standard` → `stylelint-config-standard-scss`，
`stylelint-config-recommended` → `stylelint-config-recommended-vue`。
本项目装的是 scss 方言版本。

- [ ] **Step 3: 确认 eslint 配置引用的 auto-import 声明路径正确**

`eslint.config.mjs` 会读 `./.eslintrc-auto-import.json`。该文件由 Task 2 配置的 AutoImport
插件在首次 `vite` 运行时生成。若此时文件不存在，先跑一次 `npx vite build --mode prod`
（即使失败也会生成），或临时写入 `{"globals":{}}`。

- [ ] **Step 4: 验证工具链能启动**

```powershell
npx eslint --version
npx stylelint --version
npx prettier --version
npm run lint:eslint:check
```

预期：三个 `--version` 正常输出。`lint:eslint:check` 会因旧业务代码报大量错误——
**不要修**，旧代码在后续任务中会被整体替换。只要不是"配置文件解析失败 / 找不到插件"
这类错误即可。

---

## Task 4: 样式体系、类型目录与工具函数

**Files:**
- Create: `darknight/dashboard/src/styles/{index.scss,variables.scss,global.module.scss,theme.scss,var.css}`
- Create: `darknight/dashboard/uno.config.ts`
- Create: `darknight/dashboard/src/plugins/unocss/index.ts`
- Create: `darknight/dashboard/types/{components.d.ts,env.d.ts,global.d.ts,router.d.ts}`
- Create: `darknight/dashboard/src/types/*.d.ts`
- Create: `darknight/dashboard/src/utils/{auth,color,domUtils,formatTime,formatter,is,index,propTypes,routerHelper,tree,tsxHelper}.ts`
- Delete: `darknight/dashboard/src/styles/index.scss`（旧的）、`darknight/dashboard/src/env.d.ts`

**Interfaces:**
- Produces:
  - `getAccessToken(): string | null`、`setToken(token: string): void`、`removeToken(): void` from `@/utils/auth`
  - `useDesign()` 依赖的 `global.module.scss` 的 `:export { namespace }`
  - 现有 `shared/lib/date.ts` / `format.ts` 的全部导出，签名不变，迁到 `@/utils/formatTime` 与 `@/utils/formatter`

- [ ] **Step 1: 移植样式与 UnoCSS**

```powershell
cd e:\kai\DarKnight\darknight\dashboard
Remove-Item src\styles\index.scss
Copy-Item e:\kai\yudao-ref\src\styles\* src\styles\ -Recurse -Force
Copy-Item e:\kai\yudao-ref\uno.config.ts .
Copy-Item e:\kai\yudao-ref\src\plugins\unocss src\plugins\unocss -Recurse
```

删掉 `src/styles/FormCreate/`（本项目不用 formCreate）以及 `index.scss` 中对它的 import。

- [ ] **Step 2: 移植两层类型目录**

```powershell
Copy-Item e:\kai\yudao-ref\types\*.d.ts types\ -Force
Copy-Item e:\kai\yudao-ref\src\types\*.d.ts src\types\ -Force
Remove-Item src\env.d.ts
Remove-Item types\dom7.d.ts, types\wangeditor-types.d.ts, types\svg-icons-register.d.ts -ErrorAction SilentlyContinue
```

`dom7.d.ts` 与 `wangeditor-types.d.ts` 是 yudao 为 Swiper 和 wangEditor 准备的，
`svg-icons-register.d.ts` 是 svg sprite 方案的虚拟模块声明，三者本项目都不需要（见决策记录 D1）。

改写 `types/env.d.ts` 的 `ImportMetaEnv`，只保留本项目的变量：

```ts
interface ImportMetaEnv {
  readonly VITE_APP_TITLE: string
  readonly VITE_PORT: string
  readonly VITE_OPEN: string
  readonly VITE_BASE_PATH: string
  readonly VITE_OUT_DIR: string
  readonly VITE_BASE_URL: string
  readonly VITE_API_URL: string
  readonly VITE_API_PROXY_TARGET: string
  readonly VITE_DROP_DEBUGGER: string
  readonly VITE_DROP_CONSOLE: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
```

- [ ] **Step 3: 移植工具函数**

```powershell
Copy-Item e:\kai\yudao-ref\src\utils\color.ts, e:\kai\yudao-ref\src\utils\domUtils.ts, e:\kai\yudao-ref\src\utils\is.ts, e:\kai\yudao-ref\src\utils\index.ts, e:\kai\yudao-ref\src\utils\propTypes.ts, e:\kai\yudao-ref\src\utils\routerHelper.ts, e:\kai\yudao-ref\src\utils\tree.ts, e:\kai\yudao-ref\src\utils\tsxHelper.ts, e:\kai\yudao-ref\src\utils\formatTime.ts, e:\kai\yudao-ref\src\utils\formatter.ts src\utils\
```

`utils/index.ts` 与 `formatter.ts` 里若 import 了 `@/utils/dict`、`@/utils/constants`（字典/租户相关），把对应函数删掉。

- [ ] **Step 4: 写 `src/utils/auth.ts`**

以 `e:\kai\yudao-ref\src\utils\auth.ts` 为蓝本，**删掉** refresh token、租户、
登录表单缓存、RSA 加密相关的全部导出，只留：

```ts
import { useCache } from '@/hooks/web/useCache'

const { wsCache } = useCache()

const AccessTokenKey = 'ACCESS_TOKEN'

export const getAccessToken = (): string | null => {
  return wsCache.get(AccessTokenKey)
}

export const setToken = (token: string) => {
  wsCache.set(AccessTokenKey, token)
}

export const removeToken = () => {
  wsCache.delete(AccessTokenKey)
}

export const formatToken = (token: string): string => {
  return 'Bearer ' + token
}
```

同时移植 `e:\kai\yudao-ref\src\hooks\web\useCache.ts`（`web-storage-cache` 的封装）到
`src/hooks/web/useCache.ts`——`auth.ts` 依赖它。

- [ ] **Step 5: 迁移日期与格式化工具**

现有 `src/shared/lib/date.ts` 与 `src/shared/lib/format.ts` 里的函数**原样**追加到
`src/utils/formatTime.ts` 与 `src/utils/formatter.ts` 的末尾，只改 import 路径，
**不改任何函数签名或实现**——它们的输出直接影响用户可见的表格内容。
若函数名与 yudao 已有的冲突，保留本项目的实现并删掉 yudao 的同名函数。

- [ ] **Step 6: 验证**

```powershell
npx vue-tsc --noEmit 2>&1 | Select-String "src/utils|src/styles|src/types|types/"
```

预期：无输出。全量 `ts:check` 此时必然有旧业务代码的错误，忽略。

---

## Task 5: HTTP 层

**Files:**
- Create: `darknight/dashboard/src/config/axios/{config.ts,service.ts,errorCode.ts,index.ts}`

**Interfaces:**
- Produces: `src/config/axios/index.ts` 的默认导出对象，方法 `get/post/put/delete/download/upload`，
  调用形如 `request.get<T>({ url, params })`，**直接 resolve 成后端返回的裸 JSON**。

- [ ] **Step 1: 移植四个文件**

```powershell
cd e:\kai\DarKnight\darknight\dashboard
New-Item -ItemType Directory -Force -Path src\config\axios
Copy-Item e:\kai\yudao-ref\src\config\axios\*.ts src\config\axios\
```

- [ ] **Step 2: 改写 `config.ts`**

baseURL 改成 yudao 的双变量拼接，其余 yudao 特有逻辑删除：

```ts
const config: AxiosConfig = {
  base_url: import.meta.env.VITE_BASE_URL + import.meta.env.VITE_API_URL,
  request_timeout: 60000,
  default_headers: 'application/json'
}

export { config }
```

删掉 `result_code`（本项目无业务码）。

- [ ] **Step 3: 改写 `errorCode.ts` 为 HTTP 状态码映射**

```ts
export default {
  '400': '请求参数错误',
  '401': '认证失败，无法访问系统资源',
  '403': '当前操作没有权限',
  '404': '访问资源不存在',
  '422': '请求参数校验失败',
  '500': '服务器内部错误',
  '502': '网关错误',
  '503': '服务不可用',
  default: '请求失败，请稍后重试'
} as Record<string, string>
```

- [ ] **Step 4: 改写 `service.ts`**

删掉 yudao 的租户 header、接口加解密、refresh token 队列、演示环境提示、
`{code,data,msg}` 信封判定。保留 axios 实例创建与拦截器骨架：

```ts
import axios, { type AxiosError, type AxiosResponse, type InternalAxiosRequestConfig } from 'axios'
import qs from 'qs'
import { ElMessage } from 'element-plus'
import { config } from './config'
import errorCode from './errorCode'
import { getAccessToken, removeToken, formatToken } from '@/utils/auth'

const { base_url, request_timeout } = config

export const isRelogin = { show: false }

const service = axios.create({
  baseURL: base_url,
  timeout: request_timeout,
  withCredentials: false
})

service.interceptors.request.use(
  (cfg: InternalAxiosRequestConfig) => {
    const isToken = (cfg.headers || {}).isToken !== false
    const token = getAccessToken()
    if (token && isToken) {
      cfg.headers.Authorization = formatToken(token)
    }
    if (
      cfg.method?.toUpperCase() === 'POST' &&
      cfg.headers['Content-Type'] === 'application/x-www-form-urlencoded'
    ) {
      cfg.data = qs.stringify(cfg.data)
    }
    return cfg
  },
  (error: AxiosError) => Promise.reject(error)
)

function extractMessage(error: AxiosError<any>): string {
  const detail = error.response?.data?.detail
  if (Array.isArray(detail)) {
    return detail
      .map((d: any) => {
        const field = Array.isArray(d.loc) ? d.loc[d.loc.length - 1] : ''
        return field ? `${field}: ${d.msg}` : d.msg
      })
      .join('; ')
  }
  if (typeof detail === 'string') return detail
  const status = error.response?.status
  return (status && errorCode[String(status)]) || errorCode.default
}

service.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      removeToken()
      if (!window.location.hash.startsWith('#/login')) {
        window.location.hash = '#/login'
      }
      return Promise.reject(error)
    }
    ElMessage.error(extractMessage(error as AxiosError<any>))
    return Promise.reject(error)
  }
)

export default service
```

401 分支**不弹 ElMessage**——守卫会跳登录页，再提示是噪音。

- [ ] **Step 5: 改写 `index.ts` 去掉信封解包**

yudao 的 `index.ts` 每个方法都 `return res.data`（从 envelope 里取 `data` 字段）。
本项目后端返回裸 JSON，`response.data` 就是业务数据，所以：

```ts
import service from './service'

const request = (option: any) => {
  const { url, method, params, data, headersType, responseType, headers } = option
  return service({
    url,
    method,
    params,
    data,
    responseType,
    headers: {
      'Content-Type': headersType || config.default_headers,
      ...headers
    }
  })
}

export default {
  get: async <T = any>(option: any): Promise<T> => {
    const res = await request({ method: 'GET', ...option })
    return res.data as T
  },
  post: async <T = any>(option: any): Promise<T> => {
    const res = await request({ method: 'POST', ...option })
    return res.data as T
  },
  put: async <T = any>(option: any): Promise<T> => {
    const res = await request({ method: 'PUT', ...option })
    return res.data as T
  },
  delete: async <T = any>(option: any): Promise<T> => {
    const res = await request({ method: 'DELETE', ...option })
    return res.data as T
  },
  download: async <T = any>(option: any): Promise<T> => {
    const res = await request({ method: 'GET', responseType: 'blob', ...option })
    return res as unknown as T
  },
  upload: async <T = any>(option: any): Promise<T> => {
    option.headersType = 'multipart/form-data'
    const res = await request({ method: 'POST', ...option })
    return res.data as T
  }
}
```

注意：这里 `res` 是 axios 的完整 `AxiosResponse`（响应拦截器直接 `return response`），
所以取 `res.data` 拿到的正是 FastAPI 的裸 JSON。**只解一层**，这是与 yudao 最关键的差异。

- [ ] **Step 6: 验证**

```powershell
npx vue-tsc --noEmit 2>&1 | Select-String "src/config"
```

预期：无输出。

---

## Task 6: i18n

**Files:**
- Create: `darknight/dashboard/scripts/flat-locale-to-nested.mjs`（用完即删）
- Create: `darknight/dashboard/src/locales/{en.ts,zh-CN.ts,ru.ts,fa.ts}`
- Create: `darknight/dashboard/src/plugins/vueI18n/index.ts`
- Create: `darknight/dashboard/src/hooks/web/useI18n.ts`
- Delete: `darknight/dashboard/src/locales/{en,zh,ru,fa}.json`、`src/app/i18n.ts`

**Interfaces:**
- Produces: `setupI18n(app: App): Promise<void>` from `@/plugins/vueI18n`；`useI18n()` from `@/hooks/web/useI18n`；语言标识 `en` / `zh-CN` / `ru` / `fa`

- [ ] **Step 1: 写扁平转嵌套脚本**

`darknight/dashboard/scripts/flat-locale-to-nested.mjs`：

```js
import { readFileSync, writeFileSync } from 'node:fs'
import { resolve, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const here = dirname(fileURLToPath(import.meta.url))
const localesDir = resolve(here, '../src/locales')

const files = [
  ['en.json', 'en.ts'],
  ['zh.json', 'zh-CN.ts'],
  ['ru.json', 'ru.ts'],
  ['fa.json', 'fa.ts']
]

function nest(flat) {
  const out = {}
  for (const [key, value] of Object.entries(flat)) {
    const parts = key.split('.')
    let cur = out
    parts.forEach((part, i) => {
      if (i === parts.length - 1) {
        if (typeof cur[part] === 'object' && cur[part] !== null) {
          throw new Error(`key collision (leaf over branch): ${key}`)
        }
        cur[part] = value
      } else {
        if (typeof cur[part] === 'string') {
          throw new Error(`key collision (branch over leaf): ${key}`)
        }
        if (typeof cur[part] !== 'object' || cur[part] === null) cur[part] = {}
        cur = cur[part]
      }
    })
  }
  return out
}

for (const [src, dest] of files) {
  const flat = JSON.parse(readFileSync(resolve(localesDir, src), 'utf8'))
  const nested = nest(flat)
  writeFileSync(resolve(localesDir, dest), `export default ${JSON.stringify(nested, null, 2)}\n`, 'utf8')
  console.log(`${src} -> ${dest}`)
}
```

- [ ] **Step 2: 运行并清理**

```powershell
cd e:\kai\DarKnight\darknight\dashboard
node scripts\flat-locale-to-nested.mjs
Remove-Item src\locales\en.json, src\locales\zh.json, src\locales\ru.json, src\locales\fa.json
Remove-Item scripts\flat-locale-to-nested.mjs
```

预期：输出 4 行转换记录且不抛 key collision 错误。抛错则按提示手工调整原 JSON 的 key 命名后重跑。

- [ ] **Step 3: 补路由文案**

在四个语言包顶层加 `router` 节点，键为 `home` / `user` / `node` / `host` / `setting` / `login`，
四种语言各写一份。

- [ ] **Step 4: 移植 i18n 插件与 hook**

```powershell
Copy-Item e:\kai\yudao-ref\src\plugins\vueI18n src\plugins\vueI18n -Recurse
Copy-Item e:\kai\yudao-ref\src\hooks\web\useI18n.ts src\hooks\web\useI18n.ts
Copy-Item e:\kai\yudao-ref\src\hooks\web\useLocale.ts src\hooks\web\useLocale.ts
Remove-Item src\app\i18n.ts
```

在 `plugins/vueI18n/index.ts` 里加旧 locale 值的兼容映射：读取 localStorage 的
`darknight-lang`，若值为 `zh` 则映射成 `zh-CN` 并写入新的 locale store，然后删除旧 key。

- [ ] **Step 5: 验证**

```powershell
Select-String -Path src\locales\en.ts, src\locales\zh-CN.ts, src\locales\ru.ts, src\locales\fa.ts -Pattern '^  "[a-zA-Z]+": \{'
```

预期：四个文件的顶层 key 集合一致，且都是模块名（不含点号）。某语言缺顶层模块说明该语言本就缺翻译，记录但不阻塞（会 fallback 到 en）。

---

## Task 7: Store modules

**Files:**
- Create: `darknight/dashboard/src/store/index.ts`
- Create: `darknight/dashboard/src/store/modules/{app,locale,permission,tagsView,user}.ts`
- Delete: `darknight/dashboard/src/shared/stores/theme.ts`、`src/shared/lib/{authStorage,userPreferenceStorage}.ts`

**Interfaces:**
- Produces:
  - `setupStore(app: App): void` from `@/store`
  - `useUserStore()` / `useUserStoreWithOut()` → state `{ userInfo: { username, is_sudo } | null, isSetUser: boolean }`，getters `getUserInfo` / `getIsSetUser` / `getIsSudo` / `getRoles`，actions `setUserInfoAction()` / `loginOut()` / `resetState()`
  - `usePermissionStore()` / `usePermissionStoreWithOut()` → `routers` / `addRouters` / `generateRoutes()` / `setIsAddRouters(v)`
  - `useAppStore()` / `useLocaleStore()` / `useTagsViewStore()` 与 yudao 一致

- [ ] **Step 1: 移植五个 module**

```powershell
cd e:\kai\DarKnight\darknight\dashboard
Copy-Item e:\kai\yudao-ref\src\store\index.ts src\store\index.ts
Copy-Item e:\kai\yudao-ref\src\store\modules\app.ts, e:\kai\yudao-ref\src\store\modules\locale.ts, e:\kai\yudao-ref\src\store\modules\tagsView.ts src\store\modules\
```

`user.ts` 与 `permission.ts` 差异太大，下面手写。**不要**复制 `dict.ts` / `lock.ts` / `bpm/` / `mall/`。

- [ ] **Step 2: 手写 `store/modules/user.ts`**

```ts
import { defineStore } from 'pinia'
import { store } from '../index'
import { getAccessToken, removeToken } from '@/utils/auth'
import { getAdminInfoApi } from '@/api/login'
import { resetRouter } from '@/router'

interface AdminInfo {
  username: string
  is_sudo: boolean
}

interface UserState {
  userInfo: AdminInfo | null
  isSetUser: boolean
}

export const useUserStore = defineStore('user', {
  state: (): UserState => ({
    userInfo: null,
    isSetUser: false
  }),
  getters: {
    getUserInfo(): AdminInfo | null {
      return this.userInfo
    },
    getIsSetUser(): boolean {
      return this.isSetUser
    },
    getIsSudo(): boolean {
      return this.userInfo?.is_sudo === true
    },
    getRoles(): string[] {
      if (!this.userInfo) return []
      return this.userInfo.is_sudo ? ['sudo'] : ['admin']
    }
  },
  actions: {
    async setUserInfoAction() {
      if (!getAccessToken()) {
        this.resetState()
        return null
      }
      const info = await getAdminInfoApi()
      this.userInfo = info
      this.isSetUser = true
      return info
    },
    loginOut() {
      removeToken()
      resetRouter()
      this.resetState()
    },
    resetState() {
      this.userInfo = null
      this.isSetUser = false
    }
  }
})

export const useUserStoreWithOut = () => useUserStore(store)
```

`isSetUser` 与 `userInfo` **不持久化**——每次刷新都重新调 `GET /admin` 校验，
这正是守卫做服务端校验的价值所在。

- [ ] **Step 3: 手写 `store/modules/permission.ts`**

以 `e:\kai\yudao-ref\src\store\modules\permission.ts` 为骨架，把路由源从
`wsCache.get(CACHE_KEY.ROLE_ROUTERS)`（后端菜单）换成本地 `asyncRouterMap` + 角色过滤：

```ts
import { defineStore } from 'pinia'
import { cloneDeep } from 'lodash-es'
import type { RouteRecordRaw } from 'vue-router'
import { store } from '../index'
import { asyncRouterMap, remainingRouter } from '@/router'
import { useUserStoreWithOut } from './user'

interface PermissionState {
  routers: AppRouteRecordRaw[]
  addRouters: AppRouteRecordRaw[]
  isAddRouters: boolean
  menuTabRouters: AppRouteRecordRaw[]
}

function hasPermission(route: AppRouteRecordRaw, roles: string[]): boolean {
  const required = route.meta?.roles as string[] | undefined
  if (!required || required.length === 0) return true
  return required.some((r) => roles.includes(r))
}

function filterAsyncRoutes(routes: AppRouteRecordRaw[], roles: string[]): AppRouteRecordRaw[] {
  const res: AppRouteRecordRaw[] = []
  routes.forEach((route) => {
    if (!hasPermission(route, roles)) return
    const copied = { ...route }
    if (copied.children) {
      copied.children = filterAsyncRoutes(copied.children, roles)
    }
    res.push(copied)
  })
  return res
}

export const usePermissionStore = defineStore('permission', {
  state: (): PermissionState => ({
    routers: [],
    addRouters: [],
    isAddRouters: false,
    menuTabRouters: []
  }),
  getters: {
    getRouters(): AppRouteRecordRaw[] {
      return this.routers
    },
    getAddRouters(): AppRouteRecordRaw[] {
      return this.addRouters
    },
    getIsAddRouters(): boolean {
      return this.isAddRouters
    }
  },
  actions: {
    generateRoutes(): Promise<void> {
      return new Promise((resolve) => {
        const roles = useUserStoreWithOut().getRoles
        const routerMap = filterAsyncRoutes(cloneDeep(asyncRouterMap), roles)
        this.addRouters = routerMap.concat([
          {
            path: '/:path(.*)*',
            redirect: '/404',
            name: '404Page',
            meta: { hidden: true, breadcrumb: false }
          }
        ])
        this.routers = cloneDeep(remainingRouter).concat(routerMap)
        resolve()
      })
    },
    setIsAddRouters(state: boolean) {
      this.isAddRouters = state
    }
  }
})

export const usePermissionStoreWithOut = () => usePermissionStore(store)
```

- [ ] **Step 4: 精简 `app.ts` 与 `locale.ts`**

`app.ts`：`title` 默认值改成 `'DarKnight'`；删掉本项目用不到的开关（如 `footer`、
字典/租户相关）。保留 `collapse`、`layout`、`isDark`、`currentSize`、`theme`、
`tagsView`、`breadcrumb`、`logo`、`fixedHeader`、`greyMode`。

`locale.ts`：`localeMap` 扩到四项，`elLocaleMap` 引入 Element Plus 的四个语言包：

```ts
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import en from 'element-plus/es/locale/lang/en'
import ru from 'element-plus/es/locale/lang/ru'
import fa from 'element-plus/es/locale/lang/fa'

const elLocaleMap = { 'zh-CN': zhCn, en, ru, fa }

localeMap: [
  { lang: 'zh-CN', name: '简体中文' },
  { lang: 'en', name: 'English' },
  { lang: 'ru', name: 'Русский' },
  { lang: 'fa', name: 'فارسی' }
]
```

- [ ] **Step 5: 删除旧 store 与存储工具**

```powershell
Remove-Item src\shared\stores\theme.ts, src\shared\lib\authStorage.ts, src\shared\lib\userPreferenceStorage.ts
```

旧业务代码会因此报错，这是预期的。

- [ ] **Step 6: 验证**

```powershell
npx vue-tsc --noEmit 2>&1 | Select-String "src/store"
```

预期：只剩指向 `@/router`、`@/api/login` 的"模块不存在"错误（它们在 Task 9、10 创建），
不应有其他类型错误。

---

## Task 8: 通用组件、hooks 与指令

**Files:**
- Create: `darknight/dashboard/src/components/{ContentWrap,Dialog,Pagination,Table,Form,Search,Descriptions,Icon,Qrcode,Error,ConfigGlobal}/`
- Create: `darknight/dashboard/src/hooks/web/*.ts`、`src/hooks/event/useScrollTo.ts`
- Create: `darknight/dashboard/src/directives/`
- Create: `darknight/dashboard/src/plugins/{elementPlus,svgIcon,animate.css}/`
- Delete: `darknight/dashboard/src/components/{LanguageSwitch.vue,ThemeToggle.vue}`

**Interfaces:**
- Produces（后续页面依赖，签名以 yudao 为准）：
  - `<ContentWrap :title? :message? :bodyStyle?>`
  - `<Dialog v-model :title :maxHeight? :scroll? :width?>`
  - `<Pagination :total v-model:page v-model:limit @pagination>`
  - `useMessage()` → `{ info, error, success, warning, alert, notify, confirm, delConfirm, exportConfirm, prompt }`
  - `useValidator()` → `{ required, lengthRange, notSpace, notSpecialCharacters }`
  - `useDesign()` → `{ getPrefixCls, variables }`
  - `useIcon(props)`、`useEmitt()`、`useNProgress()`、`usePageLoading()`、`useTitle()`、`useTagsView()`

- [ ] **Step 1: 移植组件**

```powershell
cd e:\kai\DarKnight\darknight\dashboard\src\components
$src = 'e:\kai\yudao-ref\src\components'
'ContentWrap','Dialog','Pagination','Table','Form','Search','Descriptions','Icon','Qrcode','Error','ConfigGlobal','Backtop','CountTo','Highlight','Infotip','InputPassword' | ForEach-Object { Copy-Item "$src\$_" . -Recurse -Force }
```

**不要**复制：`DictTag`、`Verifition`、`FormCreate`、`DiyEditor`、`bpmnProcessDesigner`、
`SimpleProcessDesignerV2`、`Tinyflow`、`Crontab`、`Cropper`、`DeptSelectForm`、
`UserSelectForm`、`OperateLogV2`、`DocAlert`、`Map`、`MagicCubeEditor`、`UploadFile`、
`Editor`、`JsonEditor`（如 Setting 页需要 JSON 编辑，用 `el-input type="textarea"` 即可）、
以及其余 yudao 业务专用组件。

- [ ] **Step 2: 移植 hooks**

```powershell
cd e:\kai\DarKnight\darknight\dashboard\src\hooks
$src = 'e:\kai\yudao-ref\src\hooks'
Copy-Item "$src\event" . -Recurse -Force
'useConfigGlobal','useCrudSchemas','useDesign','useEmitt','useForm','useIcon','useMessage','useNProgress','useNow','usePageLoading','useTable','useTagsView','useTimeAgo','useTitle','useValidator','useWatermark' | ForEach-Object { Copy-Item "$src\web\$_.ts" web\ -Force }
```

`useI18n.ts`、`useLocale.ts`、`useCache.ts` 已在 Task 4、6 移植。**不要**复制 `useGuide.ts`（依赖 driver.js）、`useNetwork.ts`。

- [ ] **Step 3: 移植 directives 与 plugins**

```powershell
cd e:\kai\DarKnight\darknight\dashboard\src
Copy-Item e:\kai\yudao-ref\src\directives directives -Recurse -Force
Copy-Item e:\kai\yudao-ref\src\plugins\elementPlus plugins\elementPlus -Recurse -Force
Copy-Item 'e:\kai\yudao-ref\src\plugins\animate.css' 'plugins\animate.css' -Recurse -Force
```

**不要**移植 `src/plugins/svgIcon`（决策记录 D1）。`components/Icon` 里的
`svg-icon:` 前缀分支一并删除，只保留 iconify 分支，底层改用 `@iconify/vue` 的
`Icon` 组件（yudao 用的 `@iconify/iconify` 已停止维护，本项目未安装）。

`directives/` 里删掉 `permission/hasPermi.ts`（依赖后端下发的细粒度权限码），
保留 `hasRole.ts` 并改写为检查 `userStore.getIsSudo`，或直接删除整个 `permission/` 子目录
并在页面里用 `v-if="userStore.getIsSudo"`。选后者，更简单。

- [ ] **Step 4: 剥离字典依赖**

`useCrudSchemas.ts` 里有四处 `dictType` 分支（`filterSearchSchema`、`filterTableSchema`、
`filterFormSchema`、`filterDescriptionsSchema`），全部删除，同时删掉对 `@/utils/dict`
与 `DictTag` 的 import，以及 `CrudSchema` 类型上的 `dictType` / `dictClass` 字段。

本项目页面不使用这个 hook，但它是 yudao 目录结构的一部分，保留且必须能编译通过。

- [ ] **Step 5: 删除旧的两个开关组件**

```powershell
Remove-Item src\components\LanguageSwitch.vue, src\components\ThemeToggle.vue
```

- [ ] **Step 6: 逐个消解类型错误**

```powershell
npx vue-tsc --noEmit 2>&1 | Select-String "src/(components|hooks|directives|plugins)"
```

常见错误来源是移植进来的文件 import 了未复制的模块（`@/store/modules/dict`、
`@/utils/dict`、`@/components/DictTag`、`@/api/...` 等）。处理原则是**删引用而非补文件**：
凡是指向本项目不需要的功能，把对应分支或整个函数删掉。

反复运行直到该命令无输出。

---

## Task 9: Layout

**Files:**
- Create: `darknight/dashboard/src/layout/Layout.vue` + `src/layout/components/**`
- Delete: `darknight/dashboard/src/components/layout/DashboardLayout.vue`

**Interfaces:**
- Produces: `Layout` 组件作为异步路由的父容器；`AppView` 内通过 `<router-view>` 渲染子路由并配合 tagsView 做 keep-alive。

- [ ] **Step 1: 移植整个 layout**

```powershell
cd e:\kai\DarKnight\darknight\dashboard
Copy-Item e:\kai\yudao-ref\src\layout src\layout -Recurse -Force
```

- [ ] **Step 2: 裁剪 yudao 专有入口**

`layout/components/ToolHeader` 及其子组件里删除：租户切换、消息通知、DocAlert 文档提示、
全局搜索（`RouterSearch` 依赖后端菜单）、指向 yudao 官网/文档的外链。

**保留**：面包屑 Breadcrumb、折叠按钮、Screenfull 全屏、SizeDropdown 尺寸切换、
LocaleDropdown 语言下拉、ThemeSwitch 主题切换、UserInfo 用户下拉。

`UserInfo` 的登出接到 `useUserStore().loginOut()` + `router.replace('/login')`，
删除"个人中心"等指向不存在页面的菜单项。

- [ ] **Step 3: Logo 与标题**

`layout/components/Logo` 中的图片改为 `/statics/logo.png`（该文件已存在于
`src/public/statics/logo.png`），标题取 `appStore.getTitle`。

- [ ] **Step 4: 删除旧 Layout**

```powershell
Remove-Item -Recurse -Force src\components\layout
```

旧 `DashboardLayout.vue` 在 `onMounted` 里调 `GET /admin` 取管理员用户名——
该职责移到 `permission.ts` 守卫（Task 10），不保留。

- [ ] **Step 5: 验证**

```powershell
npx vue-tsc --noEmit 2>&1 | Select-String "src/layout"
```

预期：只剩指向 `@/router` 的"模块不存在"错误（Task 10 创建）。

---

## Task 10: 路由、守卫、应用入口与登录页

**Files:**
- Create: `darknight/dashboard/src/router/index.ts`、`src/router/modules/remaining.ts`
- Create: `darknight/dashboard/src/permission.ts`
- Create: `darknight/dashboard/src/api/login/index.ts`
- Create: `darknight/dashboard/src/views/Login/index.vue`、`src/views/Login/components/LoginForm.vue`
- Create: `darknight/dashboard/src/views/Error/404.vue`
- Create: `darknight/dashboard/src/views/{Home,User,Node,Host,Setting}/index.vue`（占位）
- Modify: `darknight/dashboard/src/main.ts`、`src/App.vue`、`index.html`
- Delete: `darknight/dashboard/src/app/`、`src/components/login/`

**Interfaces:**
- Consumes: Task 5 的 `request`、Task 7 的 store、Task 9 的 `Layout`
- Produces:
  - `remainingRouter` / `asyncRouterMap` / `resetRouter()` / `setupRouter(app)` from `@/router`
  - `loginApi(data): Promise<{ access_token: string; token_type: string }>`、`getAdminInfoApi(): Promise<{ username: string; is_sudo: boolean }>` from `@/api/login`

- [ ] **Step 1: 核对后端登录接口**

打开 `darknight/api/v1/routers/admin.py`，确认登录端点的实际路径、请求体格式
（OAuth2 密码流 → `application/x-www-form-urlencoded`）、响应字段名，以及
`GET /admin` 的响应字段。下一步的代码以实际后端为准。

- [ ] **Step 2: 写 `src/api/login/index.ts`**

```ts
import request from '@/config/axios'

export interface LoginParams {
  username: string
  password: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
}

export interface AdminInfo {
  username: string
  is_sudo: boolean
}

export const loginApi = (data: LoginParams): Promise<TokenResponse> =>
  request.post({
    url: '/admin/token',
    data,
    headersType: 'application/x-www-form-urlencoded'
  })

export const getAdminInfoApi = (): Promise<AdminInfo> => request.get({ url: '/admin' })
```

- [ ] **Step 3: 写 `src/router/modules/remaining.ts`**

导出 `remainingRouter: AppRouteRecordRaw[]`，含 `/`（redirect 到 `/home/index`）、
`/login`（`meta: { hidden: true, title: t('router.login'), noTagsView: true }`）、
`/404`。命名沿用 yudao 风格。

- [ ] **Step 4: 写 `src/router/index.ts`**

```ts
import type { App } from 'vue'
import type { RouteRecordRaw } from 'vue-router'
import { createRouter, createWebHashHistory } from 'vue-router'
import remainingRouter from './modules/remaining'

const Layout = () => import('@/layout/Layout.vue')

export const asyncRouterMap: AppRouteRecordRaw[] = [
  {
    path: '/home',
    component: Layout,
    redirect: '/home/index',
    name: 'Home',
    meta: {},
    children: [
      {
        path: 'index',
        component: () => import('@/views/Home/index.vue'),
        name: 'HomeIndex',
        meta: { title: 'router.home', icon: 'ep:home-filled', noCache: false, affix: true }
      }
    ]
  },
  {
    path: '/user',
    component: Layout,
    redirect: '/user/index',
    name: 'User',
    meta: {},
    children: [
      {
        path: 'index',
        component: () => import('@/views/User/index.vue'),
        name: 'UserIndex',
        meta: { title: 'router.user', icon: 'ep:user' }
      }
    ]
  },
  {
    path: '/node',
    component: Layout,
    redirect: '/node/index',
    name: 'Node',
    meta: { roles: ['sudo'] },
    children: [
      {
        path: 'index',
        component: () => import('@/views/Node/index.vue'),
        name: 'NodeIndex',
        meta: { title: 'router.node', icon: 'ep:connection', roles: ['sudo'] }
      }
    ]
  },
  {
    path: '/host',
    component: Layout,
    redirect: '/host/index',
    name: 'Host',
    meta: { roles: ['sudo'] },
    children: [
      {
        path: 'index',
        component: () => import('@/views/Host/index.vue'),
        name: 'HostIndex',
        meta: { title: 'router.host', icon: 'ep:link', roles: ['sudo'] }
      }
    ]
  },
  {
    path: '/setting',
    component: Layout,
    redirect: '/setting/index',
    name: 'Setting',
    meta: { roles: ['sudo'] },
    children: [
      {
        path: 'index',
        component: () => import('@/views/Setting/index.vue'),
        name: 'SettingIndex',
        meta: { title: 'router.setting', icon: 'ep:setting', roles: ['sudo'] }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  strict: true,
  routes: remainingRouter as RouteRecordRaw[],
  scrollBehavior: () => ({ left: 0, top: 0 })
})

export const resetRouter = (): void => {
  const resetWhiteNameList = ['Redirect', 'Login', 'NoFound', 'Root']
  router.getRoutes().forEach((route) => {
    const { name } = route
    if (name && !resetWhiteNameList.includes(name as string)) {
      router.hasRoute(name) && router.removeRoute(name)
    }
  })
}

export const setupRouter = (app: App<Element>) => {
  app.use(router)
}

export { remainingRouter }
export default router
```

- [ ] **Step 5: 写 `src/permission.ts`**

以 `e:\kai\yudao-ref\src\permission.ts` 为骨架，删掉字典预加载与 `parseRouteLocation`：

```ts
import type { RouteRecordRaw } from 'vue-router'
import router from './router'
import { getAccessToken } from '@/utils/auth'
import { useTitle } from '@/hooks/web/useTitle'
import { useNProgress } from '@/hooks/web/useNProgress'
import { usePageLoading } from '@/hooks/web/usePageLoading'
import { useUserStoreWithOut } from '@/store/modules/user'
import { usePermissionStoreWithOut } from '@/store/modules/permission'

const { start, done } = useNProgress()
const { loadStart, loadDone } = usePageLoading()

const whiteList = ['/login']

router.beforeEach(async (to, from, next) => {
  start()
  loadStart()
  if (getAccessToken()) {
    if (to.path === '/login') {
      next({ path: '/' })
      return
    }
    const userStore = useUserStoreWithOut()
    const permissionStore = usePermissionStoreWithOut()
    if (userStore.getIsSetUser) {
      next()
      return
    }
    try {
      await userStore.setUserInfoAction()
      await permissionStore.generateRoutes()
      permissionStore.getAddRouters.forEach((route) => {
        router.addRoute(route as unknown as RouteRecordRaw)
      })
      permissionStore.setIsAddRouters(true)
      const redirectPath = from.query.redirect
      const redirect = typeof redirectPath === 'string' ? redirectPath : to.fullPath
      next(to.fullPath === redirect ? { ...to, replace: true } : { path: redirect, replace: true })
    } catch {
      userStore.loginOut()
      next(`/login?redirect=${encodeURIComponent(to.fullPath)}`)
    }
  } else {
    if (whiteList.indexOf(to.path) !== -1) {
      next()
    } else {
      next(`/login?redirect=${encodeURIComponent(to.fullPath)}`)
    }
  }
})

router.afterEach((to) => {
  useTitle(to?.meta?.title as string)
  done()
  loadDone()
})
```

- [ ] **Step 6: 重写 `src/main.ts`**

以 `e:\kai\yudao-ref\src\main.ts` 为蓝本，删掉 formCreate、tongji、wangEditor、
VueDOMPurifyHTML、print、setupAuth 等：

```ts
import { createApp } from 'vue'
import 'virtual:uno.css'
import '@/plugins/unocss'
import 'animate.css'
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/dark/css-vars.css'
import '@/styles/index.scss'
import { setupI18n } from '@/plugins/vueI18n'
import { setupStore } from '@/store'
import { setupGlobCom } from '@/components'
import { setupElementPlus } from '@/plugins/elementPlus'
import { setupRouter } from '@/router'
import { setupDirectives } from '@/directives'
import router from '@/router'
import App from './App.vue'
import './permission'

const setupAll = async () => {
  const app = createApp(App)
  await setupI18n(app)
  setupStore(app)
  setupGlobCom(app)
  setupElementPlus(app)
  setupRouter(app)
  setupDirectives(app)
  await router.isReady()
  app.mount('#app')
}

setupAll()
```

`await router.isReady()` 必须保留——守卫里有异步的 `GET /admin`，不等就绪会先渲染空壳再跳转。

- [ ] **Step 7: 重写 `src/App.vue`**

以 `e:\kai\yudao-ref\src\App.vue` 为蓝本，删掉 `routerSearch`，保留 `ConfigGlobal` 包裹
与暗色主题初始化。**不再设置 `dir` 属性**——这是设计文档 §4 偏离 6 声明的已知功能退化。

- [ ] **Step 8: 写登录页**

把 `src/components/login/LoginPage.vue` 的表单逻辑迁到
`src/views/Login/components/LoginForm.vue`，外层 `index.vue` 套 yudao 的登录页布局
（删掉租户输入框、验证码、社交登录、注册入口）。提交逻辑：

```ts
const handleLogin = async () => {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try {
    const res = await loginApi({ username: form.username, password: form.password })
    setToken(res.access_token)
    permissionStore.setIsAddRouters(false)
    userStore.resetState()
    const redirect = (route.query.redirect as string) || '/'
    await router.replace(redirect)
  } finally {
    loading.value = false
  }
}
```

`setIsAddRouters(false)` + `userStore.resetState()` 是关键——登录后必须让守卫按新角色
重新拉用户信息并生成路由。

- [ ] **Step 9: 404 页、占位页与 index.html**

```powershell
Copy-Item e:\kai\yudao-ref\src\views\Error\404.vue src\views\Error\404.vue -Force
```

为 `Home` / `User` / `Node` / `Host` / `Setting` 各建一个占位 `index.vue`：

```vue
<template>
  <ContentWrap>
    <div>placeholder</div>
  </ContentWrap>
</template>
```

Task 11-15 会逐个替换。`index.html` 的 `<title>` 改为 `DarKnight`，favicon 路径
`/statics/favicon/*` 保持不变。

- [ ] **Step 10: 删除旧路由与登录页**

```powershell
Remove-Item -Recurse -Force src\app, src\components\login
```

- [ ] **Step 11: 验证**

```powershell
npm run ts:check
npm run build
```

**这是第一个必须全绿的节点。**

- [ ] **Step 12: 手动验证**

先启动后端（`http://127.0.0.1:33100`），再 `npm run dev`，打开 `http://localhost:3000/`：

1. 未登录自动跳 `#/login`
2. 错误密码有报错提示
3. 正确密码登录后进入 `#/home/index`，看到 Layout 外壳与菜单
4. **非 sudo 管理员登录，菜单只有首页和用户两项**
5. 刷新页面不 404，仍停在当前路由
6. 用户下拉登出后回到登录页
7. 语言下拉能切四种语言，菜单文案跟着变
8. 主题切换能切明暗并在刷新后保持
9. 多标签页能开、能关

---

## Task 11: Home 首页

**Files:**
- Create: `darknight/dashboard/src/api/system/index.ts`
- Modify: `darknight/dashboard/src/views/Home/index.vue`（替换占位）

- [ ] **Step 1: 记录现有实现**

打开 `src/components/users/Statistics.vue`，逐项记录它调用的端点（`GET /system`）
与展示的每一个字段。字段集必须完全一致，不增不减。

- [ ] **Step 2: 写 `src/api/system/index.ts`**

按上一步的响应结构定义 `SystemStats` 接口（与接口函数同文件，yudao 惯例），导出：

```ts
import request from '@/config/axios'

export interface SystemStats {
  // 按 GET /system 的实际响应补全
}

export const getSystemStatsApi = (): Promise<SystemStats> => request.get({ url: '/system' })
```

- [ ] **Step 3: 写 `Home/index.vue`**

`ContentWrap` + `el-row`/`el-col` 卡片布局，`onMounted` 拉数据，loading 用 `el-skeleton`。
文案复用 `Statistics.vue` 已有的 i18n key，不新增翻译。

- [ ] **Step 4: 验证**

```powershell
npm run ts:check; npm run lint:eslint:check; npm run build
```

手动：登录后首页每个数字与重构前用户页顶部的统计一致。

---

## Task 12: User 模块

**Files:**
- Create: `darknight/dashboard/src/api/user/index.ts`
- Modify: `darknight/dashboard/src/views/User/index.vue`（替换占位）
- Create: `darknight/dashboard/src/views/User/UserForm.vue`、`src/views/User/QrcodeDialog.vue`、`src/views/User/utils.ts`
- Delete: `darknight/dashboard/src/components/users/`

**Interfaces:**
- Consumes: `ContentWrap`、`Pagination`、`Dialog`、`useMessage`、`useValidator`
- Produces: `src/api/user/index.ts` 的全部接口函数与类型

- [ ] **Step 1: 列端点清单**

打开 `src/components/users/api.ts`，把每一个端点列成清单。迁移时逐个打勾，
**一个都不能漏**。

- [ ] **Step 2: 写 `src/api/user/index.ts`**

把每个 vue-query composable 拆成纯接口函数，类型（原 `components/users/types.ts`）
并入同一文件。分页参数在这一层做转换——页面用 yudao 的 `pageNo`/`pageSize`，
后端要 `offset`/`limit`：

```ts
export const getUserPage = (params: UserPageParams): Promise<UserPageResult> =>
  request.get({
    url: '/users',
    params: {
      ...rest,
      offset: (params.pageNo - 1) * params.pageSize,
      limit: params.pageSize
    }
  })
```

执行前核对 `darknight/api/v1/routers/user.py` 的实际参数名。

- [ ] **Step 3: 迁移 helpers**

`src/components/users/helpers.ts` 原样搬到 `src/views/User/utils.ts`，只改 import 路径。

- [ ] **Step 4: 写 `views/User/index.vue`**

严格按 `e:\kai\yudao-ref\src\views\system\post\index.vue` 的结构：两层 `ContentWrap`
（上层搜索栏 `el-form :inline`，下层 `el-table` + `Pagination`），
`queryParams` reactive、`loading` / `list` / `total` ref，
`getList()` / `handleQuery()` / `resetQuery()` 三个方法，
`formRef.value.open(type, id)` 打开弹窗。

状态列的彩色标签用 `el-tag` 内联渲染（原来在 `UsersTable.vue` 里就是这么写的）。
删除/重置流量/撤销订阅用 `useMessage()` 的 `delConfirm` / `confirm`，
替代原来直接调 `ElMessageBox`。

- [ ] **Step 5: 写 `views/User/UserForm.vue`**

替代原 389 行的 `UserDialog.vue`。用 `Dialog` 组件包 `el-form`，
暴露 `open(type: 'create' | 'update', id?)` 方法与 `success` 事件。
校验规则用 `useValidator()` 的 `required` 等组合。

完成后确认该文件行数显著低于 389——这是本任务的核心验收指标之一。

- [ ] **Step 6: 二维码弹窗**

原 `QRCodeDialog.vue` 用 `qrcode.vue`。改成用 `Dialog` 组件包 yudao 的 `Qrcode` 组件；
若 `Qrcode` 不满足（例如需要同时展示多条订阅链接），保留 `qrcode.vue` 依赖，
只把外层换成 `Dialog`。

- [ ] **Step 7: 删除旧模块**

```powershell
Remove-Item -Recurse -Force src\components\users
```

- [ ] **Step 8: 验证**

```powershell
npm run ts:check; npm run lint:eslint:check; npm run build
```

手动逐项：列表加载、每个筛选条件、排序、翻页、改每页条数、新增、编辑、删除、
重置流量、撤销订阅、二维码内容正确、非 sudo 管理员只看到自己名下用户。

---

## Task 13: Node 模块

**Files:**
- Create: `darknight/dashboard/src/api/node/index.ts`
- Modify: `darknight/dashboard/src/views/Node/index.vue`（替换占位）
- Create: `darknight/dashboard/src/views/Node/NodeForm.vue`
- Delete: `darknight/dashboard/src/components/nodes/`

- [ ] **Step 1: 迁移接口层**

端点清单（执行前对照 `darknight/api/v1/routers/node.py` 核实）：`GET /nodes`、
`POST /node`、`GET /node/{id}`、`PUT /node/{id}`、`DELETE /node/{id}`、
`POST /node/{id}/reconnect`、`GET /nodes/usage`、`GET /node/settings`。

`GET /nodes/usage` 保留接口定义但不接 UI（本次不实现用量图）。

- [ ] **Step 2: 写 `views/Node/index.vue`**

同 Task 12 的页面模板。`GET /nodes` 返回完整数组、无分页参数，所以 `getList()`
直接把整个数组赋给 `list`、`total = list.length`，`Pagination` 做前端分页
（对数组切片）。

- [ ] **Step 3: 写 `views/Node/NodeForm.vue`**

`Dialog` + `el-form`，暴露 `open(type, id)` 与 `success` 事件。

- [ ] **Step 4: 保留重连操作**

`NodesTable.vue` 的重连按钮逻辑搬到表格操作列，成功/失败提示文案与原来一致。

- [ ] **Step 5: 删除旧模块**

```powershell
Remove-Item -Recurse -Force src\components\nodes
```

原 `nodes/store.ts` 的弹窗状态改为组件内部 ref。

- [ ] **Step 6: 验证**

```powershell
npm run ts:check; npm run lint:eslint:check; npm run build
```

手动：节点列表、新增、编辑、删除、重连、状态显示。

---

## Task 14: Host 模块

**Files:**
- Create: `darknight/dashboard/src/api/host/index.ts`
- Modify: `darknight/dashboard/src/views/Host/index.vue`（替换占位）
- Delete: `darknight/dashboard/src/components/hosts/`

- [ ] **Step 1: 迁移接口层**

两个端点：`GET /hosts`、`PUT /hosts`。响应是按 inbound tag 分组的字典。

- [ ] **Step 2: 迁移页面**

Host 页是嵌套的分组表单，**不套用列表页模板**。保持现有 `HostForm.vue` 的结构，
只做三件事：外层换成 `ContentWrap`、样式改为 SCSS + UnoCSS 原子类、
数据请求从 vue-query 改成直接调 api + 手写 `loading` ref。

- [ ] **Step 3: 严格保持字段集**

现有 `HostForm.vue` 是 153 行的简化版，缺 sockopt / fragment / noise 等高级字段，
**本次不补**。迁移前后字段逐一对照，一个不多一个不少。

- [ ] **Step 4: 删除旧模块**

```powershell
Remove-Item -Recurse -Force src\components\hosts
```

- [ ] **Step 5: 验证**

```powershell
npm run ts:check; npm run lint:eslint:check; npm run build
```

手动：主机按 inbound 分组显示正确、增删单条 host、保存后重新加载数据一致。

---

## Task 15: Setting 模块

**Files:**
- Create: `darknight/dashboard/src/api/core/index.ts`
- Modify: `darknight/dashboard/src/views/Setting/index.vue`（替换占位）
- Create: `darknight/dashboard/src/views/Setting/CoreConfig.vue`、`src/views/Setting/CoreLogs.vue`
- Delete: `darknight/dashboard/src/components/settings/`

- [ ] **Step 1: 迁移接口层**

端点：`GET /core`、`GET /core/config`、`PUT /core/config`、`POST /core/restart`。

WebSocket 日志不走 axios，把 `src/components/settings/api.ts` 的
`buildLogsWebsocketUrl()` 搬到 `src/api/core/index.ts`，其中读环境变量的部分
从 `VITE_BASE_API` 改为 `VITE_BASE_URL + VITE_API_URL`。

- [ ] **Step 2: 拆成两个子组件**

原 `SettingsPage.vue` 把配置编辑和日志流混在一起。拆成 `CoreConfig.vue`
（版本信息 + JSON 编辑 + 保存 + 重启）与 `CoreLogs.vue`（WebSocket 日志流），
`index.vue` 用 `el-tabs` 组合，每个 tab 外面套 `ContentWrap`。

JSON 编辑用 `el-input type="textarea"`，不引入 yudao 的 `JsonEditor`（它依赖
额外的编辑器库）。

- [ ] **Step 3: WebSocket 生命周期**

`CoreLogs.vue` 必须在 `onBeforeUnmount` 中关闭连接。tagsView 开启时组件会被
keep-alive 缓存，所以 `onDeactivated` 也要断开，避免后台常驻连接；
`onActivated` 重连。

- [ ] **Step 4: 删除旧模块**

```powershell
Remove-Item -Recurse -Force src\components\settings
```

- [ ] **Step 5: 验证**

```powershell
npm run ts:check; npm run lint:eslint:check; npm run build
```

手动：读取核心配置、修改并保存、重启核心、日志实时滚动、切走 tab 后连接断开、切回重连。

---

## Task 16: 收尾与全量回归

**Files:**
- Delete: `darknight/dashboard/src/shared/`
- Modify: `darknight/dashboard/README.md`（全量重写）
- Modify: `darknight/config.yaml`（注释文案）

- [ ] **Step 1: 删除残留**

```powershell
cd e:\kai\DarKnight\darknight\dashboard
Remove-Item -Recurse -Force src\shared
Get-ChildItem src -Name
```

预期 `src/` 下只剩：`api assets components config directives hooks layout locales plugins public router store styles types utils views App.vue main.ts permission.ts`。

- [ ] **Step 2: 查孤儿引用**

```powershell
rg "@tanstack/vue-query|from ['\"]ofetch|from ['\"]zod|VITE_BASE_API|@/shared/" src
```

预期：无输出。有输出说明 Task 11-15 有遗漏。

- [ ] **Step 3: 更新 config.yaml 注释**

`darknight/config.yaml` 中 `vite_base_api` 附近的注释补一句：该值会被拆分为
`VITE_BASE_URL` 与 `VITE_API_URL` 两个环境变量注入前端构建。

- [ ] **Step 4: 重写 README**

必须覆盖：新目录结构、各 npm 脚本用途、环境变量说明（含 `VITE_BASE_URL`/`VITE_API_URL`
由后端注入这件事）、产物目录是 `dist/` 且静态资源在 `dist/assets/`（提醒老环境手动删
旧的 `build/`）、与 yudao-ui-admin-vue3 的对齐关系及设计文档 §4 的六处偏离、
已知待办（RTL、Hosts 高级字段、节点用量图、保留但未使用的 echarts 依赖）。

- [ ] **Step 5: 全绿检查**

```powershell
npm run ts:check
npm run lint
npm run build
```

三条全部通过，无 error。

- [ ] **Step 6: 验证后端自动构建链路**

```powershell
cd e:\kai\DarKnight\darknight\dashboard
Remove-Item -Recurse -Force dist
cd e:\kai\DarKnight
python -m darknight
```

预期：日志出现 `Building dashboard (first run, may take a minute)...`，构建成功，
`/dashboard/` 可访问，页面资源从 `/assets/` 正常加载（浏览器开发者工具 Network
面板确认无 404）。

- [ ] **Step 7: 全量手动回归**

- [ ] 登录、登出、错误密码提示
- [ ] token 失效被守卫拦截并跳登录
- [ ] 非 sudo 管理员仅见首页与用户菜单
- [ ] 用户列表筛选、排序、分页、改每页条数
- [ ] 用户新增、编辑、删除、重置流量、撤销订阅
- [ ] 订阅二维码弹窗
- [ ] 节点列表、新增、编辑、删除、重连
- [ ] 主机分组编辑与保存
- [ ] 核心配置读取、修改、重启
- [ ] 实时日志 WebSocket 连接与断开
- [ ] 四语言切换文案完整（en / zh-CN / ru / fa）
- [ ] 明暗主题切换与持久化
- [ ] 多标签页开关、关闭、右键菜单
- [ ] 刷新任意页面不 404
- [ ] 删除 `dist/` 后 Python 首次启动自动构建并托管成功

- [ ] **Step 8: 清理参考仓库**

```powershell
Remove-Item -Recurse -Force e:\kai\yudao-ref
```

---

## 已知会中断的中间态

按顺序执行时，以下任务结束后项目**无法通过全量 `ts:check`**，这是预期的，不要试图修复：

- Task 1 后：旧代码 import 已卸载的 `ofetch` / `@tanstack/vue-query`
- Task 4 后：`main.ts` 仍 import 已删除的旧 `@/styles/index.scss`
- Task 6 后：`main.ts` 仍 import 已删除的 `@/app/i18n`
- Task 7 后：旧业务组件 import 已删除的 `@/shared/lib/authStorage` 等
- Task 8-9 后：同上

第一个必须全绿的节点是 **Task 10 Step 11**（借助五个占位页面）。
从 Task 11 起每个任务都必须全绿。

**本次不使用 git，中间态没有回滚点。** 若某个任务把项目改坏且无法恢复，
唯一的补救是从 `e:\kai\yudao-ref` 与本计划重新执行该任务。
