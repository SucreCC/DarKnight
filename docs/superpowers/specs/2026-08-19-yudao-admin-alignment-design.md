# 前端架构对齐 yudao-ui-admin-vue3 — 设计文档

- 日期：2026-08-19
- 状态：待评审（v2，参考项目已由 vue-element-plus-admin 更正为 yudao-ui-admin-vue3）
- 范围：`darknight/dashboard/`（前端）+ `darknight/dashboard/__init__.py`、`darknight/services/config/models/web.py`（后端托管适配）

## 1. 背景与目标

当前 `darknight/dashboard` 是一次自研的 Vue 3 + Element Plus 重写产物，约 42 个源文件、3472 行，
业务包含 login / users / nodes / hosts / settings 五块，目录采用 `src/components/{feature}/`
扁平组织，缺少 lint、多环境配置、路由权限等工程化设施。

本次目标：**把前端工程完全对齐 [yudao-ui-admin-vue3](https://gitee.com/yudaocode/yudao-ui-admin-vue3)
的架构风格**，主要诉求是工程规范化与可维护性。

技术栈本身不变（Vue 3 + Element Plus + Vite + Pinia + vue-i18n + TypeScript + SCSS），
改变的是工程骨架、目录约定与封装体系。

### 参考项目的识别过程（重要）

初次沟通时把参考项目误判为上游的 vue-element-plus-admin。实际核对后确认不符：
上游任何版本都没有 `build/vite/`、`src/config/axios/`、`src/types/`，环境变量也不是
`.env.local/.env.prod/.env.stage`。参考项目实为 **yudao-ui-admin-vue3**（芋道 ruoyi-vue-pro
的前端），它是 vue-element-plus-admin 的深度改造版。本文档所有结论以 yudao 的实际代码为准。

### 成功标准

1. 目录结构、命名、分层与 yudao 一致，熟悉该项目的人能直接上手。
2. 具备 ESLint / Stylelint / Prettier / 多环境配置 / 类型检查脚本。
3. 页面级 UI 状态不再进全局 store；最大文件（`UserDialog.vue` 389 行）显著瘦身。
4. 功能与重构前**严格等价**，不新增也不删减业务功能。
5. 后端 FastAPI 托管链路正常工作。

## 2. 选定方案

**原地重建骨架 + 移植参考项目核心代码。**

在现有 `darknight/dashboard/` 目录内按 yudao 规范重排结构，从 `e:\kai\yudao-ref`
逐块移植基础设施代码（axios 封装、Layout、通用组件、hooks、store modules、
SCSS + UnoCSS、lint 与构建配置），再把 5 个业务模块改写成 `views/` + `api/` 形态。

落选方案：直接 clone yudao 做底座（它带着 BPM/商城/CRM/ERP 等十余个业务子系统与字典、
租户、验证码、接口加解密等基础设施，裁剪量远大于迁移量）；只做浅层目录重排（不满足
"完全对齐"）。

## 3. 硬约束

来自后端托管链路（`darknight/dashboard/__init__.py`、`darknight/api/v1/api_worker.py`、
`darknight/services/config/models/web.py`）：

| 约束 | 说明 |
| --- | --- |
| 目录位置 | 前端必须留在 `darknight/dashboard/` |
| 路由模式 | 必须 `createWebHashHistory()`。产物由 `StaticFiles(html=True)` 挂载在 `/dashboard/`，history 模式刷新子路径会 404 |
| 构建入口 | 后端在产物不存在时自动执行 `npm run build`，该脚本必须在无额外命令行参数下产出正确结构 |
| API base 注入 | 构建时通过进程环境变量注入，值来源于 `config.yaml` 的 `web.vite_base_api` |
| 开发代理 | dev 环境保留 `/api/v1` → `http://127.0.0.1:33100` 代理 |

## 4. 相对 yudao 的偏离清单

完全照搬不可能，以下六处是**有意识的偏离**，每一处都有不可回避的理由：

| # | 偏离 | 理由 |
| --- | --- | --- |
| 1 | 用 hash 路由，yudao 用 `createWebHistory` | 后端 `StaticFiles` 静态托管，history 模式刷新子路径 404 |
| 2 | 路由表在前端静态定义并按 `is_sudo` 过滤，yudao 从后端菜单接口生成 | DarKnight 后端没有菜单接口 |
| 3 | axios 拦截器不解 `{code, data, msg}` 信封 | FastAPI 返回裸 JSON，用 HTTP 状态码 + `{detail}` 表达错误 |
| 4 | 不引入字典、租户、验证码、接口加解密、formCreate、刷新 token | 后端无对应能力 |
| 5 | 不引入 husky / lint-staged / commitlint | 本仓库是 Python 主体，前端仅为子目录，装 husky 会把前端提交规范强加给整个仓库 |
| 6 | 不做 RTL 镜像布局 | yudao 布局为 LTR 硬编码，适配需单独一轮工作 |

偏离 6 是一次**已知的功能退化**：现有 `App.vue` 在 locale 为 fa 时会设置 `dir="rtl"`，
重构后该行为移除。四语言翻译全部保留、fa 可正常切换，但界面方向统一 LTR。

## 5. 目标结构

```
darknight/dashboard/
├── build/vite/
│   ├── index.ts                # createVitePlugins(isBuild, env)
│   └── optimize.ts             # optimizeDeps 的 include / exclude
├── types/                      # 全局 d.ts
│   ├── components.d.ts  env.d.ts  global.d.ts  router.d.ts
│   └── auto-imports.d.ts
├── dist/                       # 构建产物（gitignore）
├── .env  .env.local  .env.dev  .env.prod
├── eslint.config.mjs  stylelint.config.js  prettier.config.js  postcss.config.js
├── .eslintrc-auto-import.json  .prettierignore  .stylelintignore  .editorconfig
├── uno.config.ts  vite.config.ts  tsconfig.json  index.html
├── __init__.py                 # 后端托管入口
└── src/
    ├── api/{login,user,node,host,core,system}/index.ts
    ├── assets/
    ├── components/             # 通用组件（自 yudao 移植）
    │   ├── ContentWrap/  Dialog/  Pagination/  Table/  Form/  Search/
    │   ├── Descriptions/  Icon/  Qrcode/  Error/
    ├── config/axios/{config.ts,service.ts,errorCode.ts,index.ts}
    ├── directives/
    ├── hooks/
    │   ├── event/useScrollTo.ts
    │   └── web/{useI18n,useDesign,useMessage,useValidator,useCache,useForm,useTable,
    │            useNProgress,usePageLoading,useTitle,useTagsView,useLocale,useIcon,useEmitt}.ts
    ├── layout/
    │   ├── Layout.vue
    │   └── components/{Menu,Logo,ToolHeader,TagsView,Breadcrumb,AppView,Setting,
    │                   LocaleDropdown,SizeDropdown,ThemeSwitch,Screenfull,UserInfo}/
    ├── locales/{en.ts,zh-CN.ts,ru.ts,fa.ts}
    ├── plugins/{elementPlus,unocss,vueI18n,animate.css}/
    ├── router/
    │   ├── index.ts
    │   └── modules/remaining.ts
    ├── store/
    │   ├── index.ts
    │   └── modules/{app,locale,permission,tagsView,user}.ts
    ├── styles/{index.scss,variables.scss,global.module.scss,theme.scss,var.css}
    ├── types/                  # 组件类型声明
    │   └── {components,configGlobal,descriptions,elementPlus,form,icon,
    │         layout,localeDropdown,qrcode,table,theme}.d.ts
    ├── utils/{auth,color,domUtils,formatTime,formatter,is,index,
    │           propTypes,routerHelper,tree,tsxHelper}.ts
    ├── views/{Login,Home,User,Node,Host,Setting,Error}/
    ├── App.vue
    ├── main.ts
    └── permission.ts
```

注意 yudao 有**两层类型目录**：根 `types/` 放全局声明（环境变量、路由、自动导入），
`src/types/` 放通用组件的类型声明。两者都要建。

### 范围边界

**引入**：UnoCSS、SCSS 变量体系与 `useDesign` 的 BEM 前缀、`propTypes`（vue-types）、
`@iconify` 图标、TagsView 多标签页、主题配置抽屉、Layout 多布局模式、
ESLint + Stylelint + Prettier + PostCSS、多环境 `.env`、`web-storage-cache`、
`useMessage` 消息封装。

**不引入**：yudao 的业务子系统（BPM / 商城 / CRM / ERP / MES / IM / WMS / HRM / FMS / IoT）、
字典体系（`store/modules/dict`、`utils/dict`、`DictTag`）、租户、验证码 Verifition、
接口加解密、formCreate、DocAlert、百度统计、刷新 token 队列、社交登录、
wangEditor、mock 服务、husky / lint-staged / commitlint、测试框架。

**移除**：`@tanstack/vue-query`（yudao 不用它，请求状态由页面自己的 `loading` ref 管理）、
`ofetch`（换成 axios）、`zod`（已安装但零引用）、`sass` 保留（继续用 SCSS）。

**保留但仍未使用**：`echarts` / `vue-echarts` 保留在依赖中，节点用量图本次不实现。

## 6. 页面写法：跟随 yudao 的实际模式

**关键事实**：yudao 虽然实现了 `useTable` 与 `useCrudSchemas`，但**它自己的业务页面一个都没用**
——整个仓库没有任何 `.vue` 调用 `useTable()`，`useCrudSchemas` 只在商城促销模块的
`*.data.ts` 里出现。真实的 CRUD 页走的是手写模式。

因此本次**不采用 schema 驱动**，而是跟随 yudao 的实际页面模板
`e:\kai\yudao-ref\src\views\system\post\index.vue`（232 行）：

```
<ContentWrap>                    第一层：搜索栏
  <el-form :model="queryParams" :inline="true"> ... </el-form>
  搜索 / 重置 / 新增按钮
</ContentWrap>

<ContentWrap>                    第二层：表格 + 分页
  <el-table v-loading="loading" :data="list"> ... </el-table>
  <Pagination v-model:page="queryParams.pageNo"
              v-model:limit="queryParams.pageSize"
              :total="total" @pagination="getList" />
</ContentWrap>

<XxxForm ref="formRef" @success="getList" />    独立的弹窗表单组件
```

页面脚本层的约定：`queryParams` reactive 对象承载分页与筛选、`loading` ref、
`list` / `total` ref、`getList()` / `handleQuery()` / `resetQuery()` 三个方法、
`formRef.value.open(type, id)` 打开弹窗。

`useTable` / `useCrudSchemas` 与 `Table` / `Search` 组件仍会移植进来（它们是 yudao 目录
结构的一部分），但业务页面不使用。

**分页参数命名**：yudao 用 `pageNo` / `pageSize`，DarKnight 后端 `/users` 用 `offset` / `limit`。
转换在各模块的 `api/` 层完成，页面层保持 yudao 的 `pageNo` / `pageSize` 约定。

## 7. 基础设施设计

### 7.1 HTTP 层（`src/config/axios/`）

保留 yudao 的四文件划分：`config.ts`（baseURL 与拦截器函数）、`service.ts`（axios 实例）、
`errorCode.ts`（HTTP 状态码到文案的映射）、`index.ts`（默认导出带
`get/post/put/delete/download/upload` 的对象，调用形如 `request.get({ url, params })`）。

拦截器逻辑必须改写。yudao 判断 `data.code`，并有 refresh token 队列、租户 header、
接口加解密三套逻辑；DarKnight 全部不需要：

- **请求拦截器**：注入 `Authorization: Bearer {token}`；`x-www-form-urlencoded` 时用
  `qs.stringify` 转 body（登录接口是 OAuth2 密码流，需要它）。
- **响应拦截器（成功）**：`return response.data`，不解信封。`index.ts` 的
  `get/post/...` 也相应地直接返回，不再做 `res.data` 二次解包。
- **响应拦截器（失败）**：从 `detail` 提取消息。FastAPI 422 的 `detail` 是
  `[{loc, msg, type}]` 数组，展开成字段级提示；`detail` 为字符串时直接用；
  两者皆无时回退到 `errorCode.ts` 中该 HTTP 状态码对应的文案。
- **401**：清 token，跳 `#/login`，**不弹消息**（守卫会跳转，再提示是噪音）。

`errorCode.ts` 保留但内容改写为 HTTP 状态码映射（400/401/403/404/422/500/502/503）。

WebSocket 日志（Settings 页）不走 axios，URL 构造迁到 `api/core/index.ts`，
base 读同一套环境变量。

### 7.2 环境变量

对齐 yudao 的命名，`baseURL = VITE_BASE_URL + VITE_API_URL`：

| 变量 | 用途 | 取值 |
| --- | --- | --- |
| `VITE_BASE_URL` | API 的协议+主机部分 | 相对路径时为空串；debug 模式为 `http://127.0.0.1:{port}` |
| `VITE_API_URL` | API 路径部分 | `/api/v1` |
| `VITE_BASE_PATH` | 应用部署基路径（`vite.config` 的 `base`） | `./`（产物挂在 `/dashboard/` 子路径，必须相对） |
| `VITE_OUT_DIR` | 构建产物目录 | `dist` |
| `VITE_PORT` | dev 端口 | `3000` |
| `VITE_APP_TITLE` | 站点标题 | `DarKnight` |
| `VITE_API_PROXY_TARGET` | dev 代理目标（DarKnight 新增，yudao 无） | `http://127.0.0.1:33100` |

`VITE_BASE_URL` 与 `VITE_API_URL` 由后端在构建时注入，**不写死在 `.env` 文件里**——
写进文件会覆盖进程注入值。

### 7.3 路由与权限

`src/router/index.ts` 用 `createWebHashHistory()`。静态路由沿用 yudao 的
`remainingRouter` 命名放在 `src/router/modules/remaining.ts`（登录、404、根重定向）；
业务路由用 `asyncRouterMap` 在同文件定义（这是偏离 2——yudao 从后端菜单生成）。

每条业务路由的 `meta` 沿用 yudao 的字段：`title`（i18n key）、`icon`、`hidden`、
`noCache`、`affix`、`alwaysShow`、`noTagsView`，另加 `roles: ['sudo']` 用于过滤。

`src/permission.ts` 全局前置守卫，在 yudao 版本基础上删掉字典预加载，改为：

1. 无 token 且目标非白名单 → `/login?redirect=...`
2. 有 token 且访问 `/login` → 跳 `/`
3. 有 token 且 `userStore.getIsSetUser` 为 false → 调 `GET /admin` 拿 `username`
   与 `is_sudo` 写入 `userStore`；调 `permissionStore.generateRoutes()` 按
   `is_sudo` 过滤 `asyncRouterMap`；逐条 `router.addRoute`；`next({ ...to, replace: true })`
4. `GET /admin` 失败 → 清 token 跳 `/login`

配套 NProgress 与动态标题（yudao 的 `useNProgress` / `usePageLoading` / `useTitle`）。

**角色模型**：后端已有明确的 sudo 分层——`/nodes*`、`/hosts`、`/core*`、`/users/reset`、
`/admins*` 全部依赖 `Admin.check_sudo_admin`；非 sudo 管理员的 `/users` 与 `/system`
只返回自己名下的数据。

| 路由 | 可见角色 |
| --- | --- |
| `/home` | 全部登录用户 |
| `/user` | 全部登录用户 |
| `/node` `/host` `/setting` | 仅 sudo |

这是相对现状的**行为修正**：当前前端不区分权限，非 sudo 管理员点进节点页会直接收到 403。
按钮级权限用 `v-if="userStore.getIsSudo"`，不引入 yudao 的 `v-hasPermi`（它依赖后端下发的
细粒度权限码字符串）。

### 7.4 状态管理

`src/store/modules/` 保留 yudao 的五个（去掉 `dict`、`lock` 与 bpm/mall 专用）：

| Store | 职责 | 相对 yudao 的改动 |
| --- | --- | --- |
| `app` | 布局、折叠、主题、暗色、尺寸、TagsView 开关 | 删掉本项目用不到的开关 |
| `user` | `userInfo: { username, is_sudo }`、`isSetUser`、`setUserInfoAction`、`loginOut` | 删掉 `permissions` Set 与后端菜单缓存 |
| `permission` | `routers` / `addRouters` / `generateRoutes()` | 路由源从后端菜单缓存改为本地 `asyncRouterMap` + `is_sudo` 过滤 |
| `locale` | 当前语言 + Element Plus locale | `elLocaleMap` 扩到四种语言 |
| `tagsView` | 多标签页 | 不变 |

现有 `components/users/store.ts` 与 `components/nodes/store.ts` 存的是弹窗开关、
选中行这类页面级 UI 状态，**下沉回各自 view 的组件内部**，不再进全局 store。

**token 存储**：对齐 yudao，引入 `web-storage-cache`，`src/utils/auth.ts` 导出
`getAccessToken()` / `setToken()` / `removeToken()`，key 为 `ACCESS_TOKEN`。
不实现 refresh token（后端不支持）。**副作用：现有已登录用户会被登出一次**，已确认可接受。

### 7.4b localStorage 迁移影响

主题（`darknight-theme`）、语言（`darknight-lang`）、每页条数
（`darknight-num-users-per-page`）、token（`token`）四个 key 全部变更，
用户偏好与登录态各重置一次。旧 key 不做清理。

### 7.5 i18n

现有语言包是扁平 key 的 JSON（`"login.loginYourAccount"`），转换为嵌套 TS 对象
`src/locales/{en,zh-CN,ru,fa}.ts`，与 yudao 一致。语言标识 `zh` 改为 `zh-CN`。
`src/plugins/vueI18n/index.ts` 按 yudao 的动态 import 方式加载。
`locale` store 的 `elLocaleMap` 引入 Element Plus 的 `zh-cn` / `en` / `ru` / `fa` 四个包。

### 7.6 样式

**继续用 SCSS**——yudao 用的就是 SCSS，与现有项目一致，无需转换。移植
`src/styles/{index.scss, variables.scss, global.module.scss, theme.scss, var.css}`，
`global.module.scss` 通过 `:export { namespace }` 给 `useDesign` 提供 BEM 前缀。
UnoCSS 按 yudao 的 `uno.config.ts` 配置，`presetUno({ dark: 'class' })`。
暗色模式沿用 `html.dark` / `html.light` class 切换。

现有 `src/styles/index.scss` 里的 `.dk-page` / `.dk-toolbar` / `.dk-spacer` 三个工具 class
不迁移，由 `ContentWrap` 组件与 UnoCSS 原子类取代。

## 8. 业务层迁移映射

| 现在 | 迁移后 |
| --- | --- |
| `components/login/LoginPage.vue` | `views/Login/` + `api/login/` |
| `components/users/*` | `views/User/` + `api/user/` |
| `components/users/Statistics.vue` | `views/Home/` + `api/system/`（拆为独立首页） |
| `components/nodes/*` | `views/Node/` + `api/node/` |
| `components/hosts/*` | `views/Host/` + `api/host/` |
| `components/settings/*` | `views/Setting/` + `api/core/` |
| `components/layout/DashboardLayout.vue` | 删除，由 `layout/Layout.vue` 取代 |
| `components/LanguageSwitch.vue` | `layout/components/LocaleDropdown/` |
| `components/ThemeToggle.vue` | `layout/components/ThemeSwitch/` |
| 各模块 `types.ts` | 各 `api/{module}/index.ts` 内的 interface（yudao 惯例：类型与接口同文件） |
| 各模块 `store.ts` | 组件内部状态 |
| `components/users/helpers.ts` | `views/User/utils.ts` |
| `shared/lib/date.ts` | `utils/formatTime.ts` |
| `shared/lib/format.ts` | `utils/formatter.ts` |
| `shared/lib/authStorage.ts` | `utils/auth.ts` |
| `shared/lib/userPreferenceStorage.ts` | `store/modules/app.ts` |
| `shared/stores/theme.ts` | `store/modules/app.ts` |
| `shared/api/http.ts` | `config/axios/` |

每个 view 目录按 yudao 惯例组织为 `views/User/index.vue`（页面）+
`views/User/UserForm.vue`（弹窗表单，与页面同级而非放 `components/` 子目录）。

`UserDialog.vue` 当前 389 行，是全项目最大文件，拆成 `UserForm.vue`（表单弹窗）
后应显著瘦身，作为重点验证对象。

Host 页是按 inbound tag 分组的嵌套表单，不适用列表页模板，保持自定义布局，
只把外层换成 `ContentWrap`。Setting 页是配置编辑 + 日志流，用 `el-tabs` 拆成两个子组件。

### 功能等价性

本次**不补**任何已知功能缺口，包括 Hosts 的高级字段（sockopt / fragment / noise）
与节点用量 echarts 图表。除 §7.3 的权限过滤修正、§4 偏离 6 的 RTL 退化、
§7.4 的登录态重置外，所有页面行为与重构前保持一致。

## 9. 后端改动

### `darknight/dashboard/__init__.py`

1. `build_dir = base_dir / "dist"`
2. `statics_dir = build_dir / "assets"`，挂载点从 `/statics/` 改为 `/assets/`
3. `build_dashboard()` 移除硬编码的 `--outDir` / `--assetsDir` 参数（改由 `.env` 的
   `VITE_OUT_DIR` 与 Vite 默认 `assetsDir` 控制）
4. 环境变量注入从单个 `VITE_BASE_API` 改为拆分注入 `VITE_BASE_URL` + `VITE_API_URL`

拆分规则：`web.vite_base_api` 若是相对路径（如 `/api/v1/`），则
`VITE_BASE_URL=""`、`VITE_API_URL="/api/v1"`；若是绝对 URL（debug 模式下的
`http://127.0.0.1:33100/api/v1/`），则按协议+主机与路径切开。尾部斜杠统一去掉。

### `darknight/services/config/models/web.py`

**不动**。`vite_base_api` 这个用户可见的配置项保持原样，拆分只发生在注入时，
避免破坏用户现有的 `config.yaml`。

### 其他

`darknight/dashboard/.gitignore`：`build/` 改为 `dist/`，追加 `.eslintrc-auto-import.json`。
`darknight/dashboard/README.md`：全量重写。
`darknight/config.yaml`：`vite_base_api` 相关注释文案微调（说明它会被拆分注入）。

## 10. 工程化配置

从 yudao 移植 `eslint.config.mjs`、`stylelint.config.js`、`prettier.config.js`、
`postcss.config.js`、`.editorconfig`、`.prettierignore`、`.stylelintignore`，
去掉其中指向 yudao 业务目录的忽略项。

npm scripts 对齐 yudao 的命名，但**必须保留一个无参数可用的 `build`**（后端直接调它）：

| 脚本 | 说明 |
| --- | --- |
| `dev` | `vite --mode local` |
| `build` | `vite build --mode prod`，产物落 `dist/` |
| `preview` | `vite preview` |
| `ts:check` | `vue-tsc --noEmit` |
| `lint:eslint` / `lint:style` / `lint:format` | 三条 lint，各带 `:check` 变体 |
| `lint` | 串联三条 check |

## 11. 执行阶段

| 阶段 | 内容 | 验收 |
| --- | --- | --- |
| 1. 依赖 | 卸载 vue-query / ofetch / zod，安装 axios、unocss、web-storage-cache、lint 工具链等 | `npm ls` 无 UNMET |
| 2. 构建骨架 | `build/vite/`、`vite.config.ts`、四个 `.env`、`tsconfig`、`__init__.py` 与 `.gitignore` 改动 | 能 build 出 `dist/` + `dist/assets/`，环境变量注入生效 |
| 3. Lint 工具链 | 四个配置文件 + scripts | 三条 lint 命令能启动 |
| 4. 样式与类型 | SCSS 体系、UnoCSS、根 `types/` 与 `src/types/`、`utils/` | `ts:check` 无来自这些目录的错误 |
| 5. HTTP 层 | `config/axios/` 四文件改写 | 同上 |
| 6. i18n | 四语言转嵌套 TS、`plugins/vueI18n`、`useI18n` | 四个语言包顶层 key 一致 |
| 7. Store | 五个 module | 同上 |
| 8. 组件与 hooks | 通用组件、`hooks/web/*`、`directives/` | 同上 |
| 9. Layout | 外壳全套 | 同上 |
| 10. 路由与入口 | `router/`、`permission.ts`、`main.ts`、`App.vue`、Login、404 | 能登录；sudo 与非 sudo 菜单不同；刷新不 404 |
| 11. Home | Statistics 拆为独立首页 | 数据正确 |
| 12-15. User / Node / Host / Setting | 逐模块迁移 | 每模块功能回归 |
| 16. 收尾 | 删 `shared/`、README 重写、全量回归 | 见 §12 |

## 12. 验证策略

项目无测试框架，yudao 也没有，本次不引入。自动化验收为三项命令全绿：

```
npm run ts:check
npm run lint
npm run build
```

手动回归清单：

1. 登录、登出、错误密码提示
2. token 失效被守卫拦截并跳转登录
3. 非 sudo 管理员登录后仅见首页与用户菜单
4. 用户列表筛选、排序、分页、每页条数
5. 用户新增、编辑、删除、重置流量、撤销订阅
6. 订阅二维码弹窗
7. 节点列表、新增、编辑、删除、重连
8. 主机分组编辑与保存
9. 核心配置读取、修改、重启
10. 实时日志 WebSocket 连接与断线
11. 四语言切换（en / zh-CN / ru / fa）文案完整
12. 明暗主题切换与持久化
13. 多标签页开关、关闭、右键菜单
14. 浏览器刷新任意页面不 404
15. 删除 `dist/` 后由 Python 首次启动自动构建成功并正常托管

## 13. 已知风险

| 风险 | 影响 | 缓解 |
| --- | --- | --- |
| RTL 支持退化 | fa 语言用户界面方向变为 LTR | 已确认可接受，后续单独设计 |
| 全体用户登出一次 | token key 从 `token` 变为 `ACCESS_TOKEN` | 已确认可接受 |
| 产物目录与资源目录双改名 | Python 侧未同步会导致 404 | 阶段 2 即完成 `__init__.py` 改动并验证；旧 `build/` 需手动清理 |
| 环境变量注入失效 | 生产构建拿到错误的 API base | 两个变量不写入 `.env` 文件；阶段 2 用自定义值构建并在产物中搜索验证 |
| vue-query 移除后请求状态回归 | 加载态、错误态、缓存行为变化 | 逐模块迁移，每模块单独回归 |
| yudao 组件的隐性依赖 | 通用组件可能 import 字典/租户等被裁掉的模块，导致连锁编译错误 | 阶段 8 集中移植并以 `ts:check` 全量校验，原则是删引用而非补文件 |
| 无 git 回滚点 | 中途出错只能手工回退 | 用户已确认接受；阶段 2-9 期间项目处于不可编译中间态，第一个可运行节点是阶段 10 |
