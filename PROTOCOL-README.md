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
    ├── :8443 ──► Xray VLESS + TLS  (直连，不经 nginx)
    ├── :8444 ──► Xray VMess + TLS
    ├── :8445 ──► Xray Trojan + TLS
    └── :1080 ──► Xray Shadowsocks
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

| 用途 | 记录 | 代理模式 |
| --- | --- | --- |
| 网站面板 | `darkight.com` A → VPS | 橙云（可） |
| 邮件 | `mail.darkight.com` A → VPS | 灰云（必须） |
| 代理节点 | `darkight.com:8443` 或子域如 `node.darkight.com` | **灰云**（必须） |

Cloudflare 橙云**不会**转发 8443、8444、8445、1080 等自定义端口。代理域名须灰云直连 VPS IP。

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
| VLESS TCP TLS | VPS IP 或 `node.darkight.com` | 8443 | `darkight.com` | tls |
| VMess TCP TLS | 同上 | 8444 | `darkight.com` | tls |
| Trojan TCP TLS | 同上 | 8445 | `darkight.com` | tls |
| Shadowsocks TCP | 同上 | 1080 | — | none |

用户创建 / 编辑时需勾选对应协议与 Inbound，订阅链接才会包含正确节点。

---

## 客户端连接示例

假设 VPS IP 为 `1.2.3.4`，SNI 为 `darkight.com`：

| 协议 | 地址 | 端口 | 备注 |
| --- | --- | --- | --- |
| VLESS | `1.2.3.4` 或 `node.darkight.com` | 8443 | TLS，flow 按面板生成 |
| VMess | 同上 | 8444 | TLS |
| Trojan | 同上 | 8445 | TLS |
| Shadowsocks | 同上 | 1080 | 密码/加密方式见订阅 |

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
