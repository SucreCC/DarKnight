# DarKnight 代理协议说明

本文档说明 DarKnight 支持的四种代理协议、端口规划、TLS 证书与 mailcow Nginx 的配合方式。

## 支持的协议

DarKnight 面板最多支持 **4 种**用户协议：

| 协议 | 传输 | TLS 证书 | 默认端口 | Inbound Tag |
| --- | --- | --- | --- | --- |
| VLESS | TCP | ✅ 需要 | `8443` | `VLESS TCP TLS` |
| VMess | TCP | ✅ 需要 | `8444` | `VMess TCP TLS` |
| Trojan | TCP | ✅ 需要 | `8445` | `Trojan TCP TLS` |
| Shadowsocks | TCP/UDP | ❌ 不需要 | `1080` | `Shadowsocks TCP` |

配置文件：`xray_config.json`（Docker 运行时同步到 `data/xray_config.json`）。

> 面板 UI 会列出全部 4 种协议；只有 `xray_config.json` 里存在对应 inbound 时，该协议才会真正生效。

---

## 架构：Nginx 与 Xray 分工

```text
Internet
    │
    ├── :443 ──► mailcow nginx ──► :33100  DarKnight 面板 (HTTPS)
    │            (darkight.com / mail.darkight.com)
    │
    ├── :8443 ──► Xray VLESS + TLS   node.darkight.com（灰云）
    ├── :8444 ──► Xray VMess + TLS
    ├── :8445 ──► Xray Trojan + TLS
    └── :1080 ──► Xray Shadowsocks   ss.darkight.com（灰云）
```

- **网站 / 面板**：`https://darkight.com` 由 mailcow 的 `nginx-mailcow` 在 443 终止 TLS，反代到本机 `33100`。
- **代理流量**：由 DarKnight 容器内 Xray 直接监听，**不经过 Nginx 反代**。
- **443 不能给 Xray 用**：已被 Nginx 占用，TLS 代理使用 `8443–8445`。

---

## TLS 证书

与 mailcow 共用宿主机 Let's Encrypt 证书（一张证覆盖 `darkight.com` 与 `mail.darkight.com`）：

```text
/etc/letsencrypt/live/mail.darkight.com/fullchain.pem
/etc/letsencrypt/live/mail.darkight.com/privkey.pem
```

Docker 通过只读挂载提供给容器（见 `docker-compose.yml`）：

```yaml
volumes:
  - /etc/letsencrypt:/etc/letsencrypt:ro
```

客户端连接时 **SNI 填 `darkight.com`** 即可通过校验。

### 证书续期后

mailcow 续期并复制证书后，重启 DarKnight 使 Xray 重新加载：

```bash
docker compose restart darknight
```

---

## Cloudflare / DNS

当前 VPS IP：`169.58.212.160`。

### 已配好的记录（无需修改）

| 名称 | 类型 | 内容 | 代理 | 用途 |
| --- | --- | --- | --- | --- |
| `darkight.com`（`@`） | A | `169.58.212.160` | **橙云** | 网站 / 面板 HTTPS |
| `www` | A | `169.58.212.160` | **橙云** | www 站点 |
| `mail` | A | `169.58.212.160` | **灰云** | 邮件 |
| `ss` | A | `169.58.212.160` | **灰云** | Shadowsocks（`:1080`） |
| `@` | MX | `mail.darkight.com` | — | 收信 |
| `@` / `dkim._domainkey` / `_dmarc` | TXT | SPF / DKIM / DMARC 等 | — | 邮件认证 |
| `autoconfig` / `autodiscover` | CNAME | `mail.darkight.com` | **灰云** | 邮件客户端自动配置 |

### 还需添加 1 条（VLESS / VMess / Trojan）

TLS 三类代理需要 **`node`** 子域（灰云直连 VPS，不能开橙云）：

Cloudflare → DNS → **Add record**：

| 字段 | 填什么 |
| --- | --- |
| **Type** | `A` |
| **Name** | `node` |
| **IPv4 address** | `169.58.212.160` |
| **Proxy status** | **关闭**（灰色云朵，**DNS only**） |
| **TTL** | `Auto` |

点 **Save** → 得到 `node.darkight.com`，用于 `:8443` / `:8444` / `:8445`。

> 橙云只代理 **80 / 443**，不会转发 8443 等自定义端口。`darkight.com` 已是橙云，**不能**用它连代理端口；须用灰云子域 `node` / `ss`。

### SSL/TLS 建议（Cloudflare → SSL/TLS → Overview）

| 项 | 推荐值 |
| --- | --- |
| 加密模式 | **Full (strict)** |
| 始终使用 HTTPS | 开启（可选） |

### 域名与端口对照

| 用途 | 客户端地址 | Cloudflare | 端口 |
| --- | --- | --- | --- |
| 网站 / 面板 | `https://darkight.com` | **橙云** | 443（经 CF） |
| 邮件 | `mail.darkight.com` | **灰云** | 25 / 443 等 |
| VLESS / VMess / Trojan | `node.darkight.com` | **灰云** | 8443 / 8444 / 8445 |
| Shadowsocks | `ss.darkight.com` | **灰云** | 1080 |

TLS 三类协议的 **SNI 填 `darkight.com`**（与 Let's Encrypt 证书 SAN 一致），与连接用的主机名（`node.darkight.com`）可以不同。

VPS 防火墙 / 安全组须放行：`8443`、`8444`、`8445`、`1080`（tcp/udp）。

---

## 防火墙 / 安全组

除已有 443、25（邮件）外，需放行：

| 端口 | 协议 |
| --- | --- |
| `8443` | TCP |
| `8444` | TCP |
| `8445` | TCP |
| `1080` | TCP + UDP |

`33100` 建议仅本机访问（由 Nginx 443 反代对外）。

---

## 部署

```bash
cd /path/to/DarKnight
docker compose up -d --build
```

容器启动时会：

1. 将 `xray_config.json` 同步到 `data/xray_config.json`
2. 执行数据库迁移
3. 启动面板与 Xray

---

## 管理后台 Host 配置

部署后进入 **管理后台 → Host**，为每个 inbound 添加一条主机记录（示例）：

| Inbound | 地址 | 端口 | SNI | 安全 |
| --- | --- | --- | --- | --- |
| VLESS TCP TLS | `node.darkight.com` | 8443 | `darkight.com` | tls |
| VMess TCP TLS | `node.darkight.com` | 8444 | `darkight.com` | tls |
| Trojan TCP TLS | `node.darkight.com` | 8445 | `darkight.com` | tls |
| Shadowsocks TCP | `ss.darkight.com` | 1080 | — | none |

用户创建 / 编辑时需勾选对应协议与 Inbound，订阅链接才会包含正确节点。

---

## 客户端连接示例

| 协议 | 地址 | 端口 | 备注 |
| --- | --- | --- | --- |
| VLESS | `node.darkight.com` | 8443 | TLS，SNI = `darkight.com` |
| VMess | `node.darkight.com` | 8444 | TLS，SNI = `darkight.com` |
| Trojan | `node.darkight.com` | 8445 | TLS，SNI = `darkight.com` |
| Shadowsocks | `ss.darkight.com` | 1080 | 密码 / 加密方式见订阅 |

推荐使用订阅链接导入，避免手动填错 SNI 或端口。

---

## 常见问题

**面板勾了 VMess/VLESS 但订阅里没有节点**

- 检查 `xray_config.json` 是否包含对应 inbound
- 检查 Host 是否配置了该 inbound 的地址与端口
- 重启容器：`docker compose restart darknight`

**Xray 启动失败 / 证书错误**

- 确认宿主机存在 `/etc/letsencrypt/live/mail.darkight.com/fullchain.pem`
- 确认 Docker 已挂载 `/etc/letsencrypt:ro`
- 查看日志：`docker compose logs darknight --tail 50`

**客户端报证书无效**

- SNI 必须是证书记录中的域名（`darkight.com` 或 `mail.darkight.com`）
- 不要用 IP 作 SNI（除非客户端开启 allowInsecure）

**443 上无法跑代理**

- 正常：443 留给 Nginx 面板，代理用 8443–8445

**修改 inbound 后未生效**

- 改 `xray_config.json` 后执行 `docker compose up -d --build`
- 运行时配置在 `data/xray_config.json`，镜像启动时会从仓库默认文件同步覆盖

---

## 相关文件

| 文件 | 说明 |
| --- | --- |
| `xray_config.json` | Xray 入站定义（协议、端口、证书路径） |
| `docker-compose.yml` | 端口映射与证书卷挂载 |
| `Dockerfile` | 构建时打包配置，启动时同步到 `data/` |
| [README.md](README.md) | 项目总览与快速部署 |
