# DarKnight Dashboard

DarKnight 管理面板前端，基于 **Vue 3 + Vite + Element Plus**。

## 技术栈

- Vue 3（`<script setup>` + TypeScript）
- Vite（构建 / 开发服务器）
- Element Plus（UI 组件库）
- Pinia（状态管理）
- Vue Router（hash 模式）
- @tanstack/vue-query（服务端数据）
- vue-i18n（国际化：en / zh / ru / fa）

## 环境要求

- Node.js >= 18（推荐 20+）
- npm

## 安装

```bash
cd darknight/dashboard
npm install
```

## 配置

复制 `example.env` 为 `.env`，设置后端 API 地址：

```
VITE_BASE_API=/api/v1/
```

| 变量 | 说明 |
| --- | --- |
| `VITE_BASE_API` | 后端 API 基础路径，默认 `/api/v1/` |
| `VITE_API_PROXY_TARGET` | 开发环境下 `/api/v1` 代理目标，默认 `http://127.0.0.1:33100` |

## 开发

```bash
npm run dev
```

开发服务器运行在 `http://localhost:3000`，`/api/v1` 请求会代理到后端。

## 构建

```bash
npm run build
```

产物输出到 `build/`（资源在 `build/statics/`），由后端 `darknight/dashboard/__init__.py` 作为静态文件托管。

## 类型检查

```bash
npm run type-check
```

## 目录结构

```
src/
├── app/          # 路由、i18n
├── layouts/      # 布局外壳
├── pages/        # 路由级页面
├── features/     # 业务模块（users / nodes / hosts / settings）
├── components/   # 通用组件
├── shared/       # http、工具、stores、类型
├── locales/      # 语言包
└── styles/       # 全局样式
```
