# DarKnight

基于 [Xray](https://github.com/XTLS/Xray-core) 的代理管理面板：统一提供用户门户、管理后台与 REST API，支持订阅下发、套餐下单、节点与用户运维。

## 主要能力

- 用户门户：注册登录、套餐购买、订单、邀请、工单、订阅链接
- 管理后台：用户 / 节点 / 主机 / 产品目录 / 工单等运维能力
- 订阅与协议：Clash、Sing-box、V2Ray 等客户端配置下发
- 支付与履约：订单支付、套餐履约（有效期 / 流量等）
- 邮件与通知：验证码等邮件能力（需配置 SMTP）
- 可选 Telegram Bot 管理能力

## 技术栈

| 层级 | 技术 |
| --- | --- |
| 后端 | Python 3.10+、FastAPI、SQLAlchemy、Alembic、Uvicorn |
| 前端 | Vue 3、Vite、TypeScript |
| 核心 | Xray-core |
| 部署 | Docker / Docker Compose |

## 快速部署（Docker）

要求：已安装 Docker 与 Docker Compose。

```bash
git clone <本仓库地址>
cd DarKnight
docker compose up -d --build
```

启动后：

- Web 面板：`http://<主机>:33100/`
- API 前缀：`/api/v1`
- 容器内会自动执行 `alembic upgrade head` 再启动服务

### 端口与数据

| 项目 | 说明 |
| --- | --- |
| `33100` | HTTP 面板与 API（`docker-compose.yml` 已映射） |
| `./data` | 持久化目录：数据库、日志、运行时 `xray_config.json` |

代理协议、TLS 端口与 Nginx 配合见 [PROTOCOL-README.md](PROTOCOL-README.md)。

应用配置来自镜像内的 `darknight/config.yaml`。修改配置后需要重新构建并启动：

```bash
docker compose up -d --build
```

## 配置说明

主配置文件：`darknight/config.yaml`（可通过环境变量覆盖部分项，如 `UVICORN_HOST`、`UVICORN_PORT`）。

常见配置块：

- `server`：监听地址与端口（默认 `33100`）
- `database`：数据库连接（本地默认 SQLite；Docker 镜像内为 `/app/data/db.sqlite3`）
- `xray`：可执行文件、资源路径、订阅前缀等
- 邮件 / Telegram 等：按需填写，未配置时相关能力不可用

本地开发默认数据库为仓库根目录下的 `db.sqlite3`；Docker 部署使用挂载卷 `./data`。

## 本地开发（摘要）

### 后端

```bash
# 建议使用虚拟环境
pip install -r requirements.txt
pip install -e .

# 数据库迁移
alembic upgrade head

# 启动（需本机已准备好 Xray，路径见 config.yaml）
python -m darknight.main
```

默认监听 `http://127.0.0.1:33100`。

### 前端

```bash
cd darknight/dashboard
npm install
npm run dev
```

开发服务器默认在 `http://localhost:3000`，`/api/v1` 会代理到后端。更完整的前端说明见 [darknight/dashboard/README.md](darknight/dashboard/README.md)。

生产构建产物由后端托管；Docker 镜像构建阶段已执行 `npm run build`。

## 目录结构

```text
DarKnight/
├── darknight/           # 后端应用、配置、前端源码与构建产物
│   ├── api/             # FastAPI 路由与依赖
│   ├── dashboard/       # Vue 前端
│   ├── db/              # 模型、CRUD、Alembic 迁移
│   ├── services/        # 支付、邮件等业务服务
│   └── config.yaml      # 主配置
├── xray_api/            # Xray gRPC / protobuf 封装
├── scripts/             # 节点脚本、Xray 安装等
├── docs/                # 设计与实现文档
├── docker-compose.yml
├── Dockerfile
├── PROTOCOL-README.md
├── README.md
├── alembic.ini
└── requirements.txt
```

## 相关文档

- [代理协议说明](PROTOCOL-README.md)
- [前端 Dashboard](darknight/dashboard/README.md)
- [节点与辅助脚本](scripts/README.md)
- [数据库迁移说明](darknight/db/migrations/README)
