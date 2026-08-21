# 多账号事务邮件发送服务 — 设计文档

- 日期：2026-08-21
- 状态：待评审
- 范围：`darknight/services/mail/`、`darknight/services/config/models/email.py`、`darknight/config.yaml`、`darknight/db`（新增 `email_outbox`）、`darknight/utils/email_sender.py`、`darknight/api/v1/routers/auth.py`

## 1. 背景与目标

门户注册已通过 SMTP 发送邮箱验证码。当前实现为单账号扁平配置 + `send_verification_email()` 同步直发，无法支撑：

- 多个发件身份（`noreply@darkight.com`、`support@darkight.com`）
- 可复用的 HTML + 纯文本模板
- 异步发送、失败可查与有限重试

本次目标：设计一套可后续扩展的事务邮件服务，先落地验证码场景，并为欢迎信、重置密码等预留同一入口。

### 成功标准

1. 业务代码按账号别名（`noreply` / `support`）发信，不硬编码 SMTP 凭证。
2. 统一入口支持模板渲染（HTML + plaintext）、入队异步发送、outbox 可观测。
3. 注册发码主流程不因 SMTP 瞬时失败而失败（验证码已入库）。
4. `dev_log_only` 下不连真实 SMTP，便于本地开发。
5. 现有 `email_verification_codes` 职责不变；投递状态落在独立 `email_outbox`。

## 2. 选定方案

**轻量 MailService + 账号 Profile + 进程内异步 + Outbox。**

不引入 Redis/Celery。使用 FastAPI `BackgroundTasks`（或等价线程池）执行 SMTP；以数据库 outbox 作为发送事实来源与重启补发依据。

备选曾考虑：仅封装 SMTP（缺模板/重试层）、独立邮件 worker（运维过重）。均不采用。

## 3. 架构

```
业务代码 (auth / 后续订单·客服…)
        │
        ▼
   MailService.enqueue / send_now(template, account, to, context)
        │  1) 解析账号 profile
        │  2) Jinja2 渲染 subject / text / html
        │  3) 写入 email_outbox (pending)
        │  4) BackgroundTasks 真正 SMTP 发送
        ▼
   SmtpTransport (按 account 登录、STARTTLS)
        │
        ▼
   更新 outbox → sent / failed（未达上限则重试）
```

### 组件边界

| 组件 | 职责 |
|------|------|
| `MailService` | 唯一对外入口：选账号、渲染、入队、触发发送/重试 |
| `SmtpTransport` | 仅负责 SMTP 连接、登录、发信 |
| Templates | 文件系统 Jinja2：每主题三件套 |
| `email_outbox` | 投递生命周期与排障数据 |

## 4. 配置

在 `config.yaml` 的 `email` 段扩展为共享 SMTP + 多 account：

```yaml
email:
  smtp_host: mail.darkight.com
  smtp_port: 587
  use_tls: true
  dev_log_only: false
  default_account: noreply
  max_attempts: 3
  accounts:
    noreply:
      smtp_user: noreply@darkight.com
      smtp_password: "***"
      from_address: noreply@darkight.com
      from_name: Darkight
    support:
      smtp_user: support@darkight.com
      smtp_password: "***"
      from_address: support@darkight.com
      from_name: Darkight Support
```

### 约定

- `host` / `port` / `use_tls` 全局共享（同一邮件服务器）。
- 业务只使用别名 `noreply` / `support`；未指定时用 `default_account`。
- 密码仅存配置/密钥管理，不进代码。
- 兼容：旧扁平字段 `smtp_user` / `smtp_password` / `from_address` 映射为默认 `noreply` account，避免一次升级挂掉。

`EmailConfig` dataclass 相应扩展；`AppConfig` 加载路径不变。

## 5. 对外 API 与模板

### API

```python
from darknight.services.mail import mail

mail.enqueue(
    template="verification_code",
    to="user@example.com",
    context={"code": "123456", "expire_minutes": 5},
    account="noreply",  # 可省略 → default_account
)

mail.send_now(...)  # 同步；供脚本/管理命令
```

- `enqueue`：渲染 → 写 outbox → 交后台发送；返回 `outbox_id`（或等价结果对象）。
- 注册验证码改为走 `enqueue`；废弃业务直接依赖旧 `send_verification_email` 实现细节（可保留薄封装转发）。

### 模板

目录：`darknight/services/mail/templates/`

每主题三文件（Jinja2）：

- `{name}.subject.txt`
- `{name}.txt`
- `{name}.html`

首批仅落地 `verification_code`。后续主题（welcome、password_reset 等）按同一约定添加，无需改服务核心。

项目已依赖 Jinja2，直接使用。

## 6. 数据库

### 原则：两表分离，不合并

| 表 | 职责 |
|----|------|
| `email_verification_codes`（已有） | 认证凭证：码、过期、冷却查询 |
| `email_outbox`（新建） | 投递过程：pending/sent/failed、重试、错误 |

业务流程串联（先写验证码，再 enqueue 邮件），用同一 `email`/`to_address` 关联即可，**不设强制外键**。

不改 `users` 及其他业务表。

### 新建表 `email_outbox`

| 列 | 说明 |
|----|------|
| `id` | 主键 |
| `account` | 账号别名 |
| `template` | 模板名 |
| `to_address` | 收件人（建议 index） |
| `subject` | 渲染后主题 |
| `body_text` | 渲染后纯文本 |
| `body_html` | 渲染后 HTML（可空） |
| `status` | `pending` / `sending` / `sent` / `failed`（建议 index） |
| `attempts` | 已尝试次数，默认 0 |
| `max_attempts` | 默认取配置 `email.max_attempts`（3） |
| `last_error` | 最近错误摘要 |
| `created_at` / `updated_at` | 时间戳 |
| `sent_at` | 成功发送时间（可空） |

建议复合索引：`(status, created_at)`，便于补发扫描。

**存储渲染结果**（非仅 context JSON），避免模板改版后重试内容不一致。

一次 Alembic 迁移建表即可；无回填、无破坏性变更。

## 7. 发送、重试与错误处理

1. `enqueue`：渲染 → 插入 `pending` → `BackgroundTasks`。
2. 同一后台任务内：`pending` → `sending` → SMTP；失败则 `attempts++`，未达 `max_attempts` 时短暂 sleep 后重试，耗尽则 → `failed` + `last_error`；成功 → `sent` + `sent_at`。
3. 进程重启：启动时或既有 jobs 扫描卡住的 `pending`/`sending`（例如进程在发送中被杀掉），对 `attempts < max_attempts` 的记录再次派发。

### 错误策略

- SMTP/网络异常：记 outbox，**不**回抛到注册 HTTP 主路径（验证码已落库）。
- 配置缺失 / 未知 account / 模板不存在：`enqueue` 时立即失败并打日志（部署错误，应尽早暴露）。若 auth 在写验证码之后才 enqueue，需捕获该类异常并打错误日志，仍可对客户端返回「已发送」（验证码有效）；也可选择在写库前先校验模板/账号——实现时优先「写库前校验配置与模板」，避免无信可发的验证码。
- `dev_log_only=true`：不连 SMTP，打日志，outbox 状态记为 `sent`（`sent_at` 置当前时间）。

### 明确不做（YAGNI）

- 不做 outbox 管理后台 UI。
- 不做独立「重发邮件」API（验证码场景沿用现有 send-code 冷却）。
- 不引入外部消息队列。

## 8. 文件布局与迁移路径

```
darknight/services/mail/
  __init__.py
  service.py
  transport.py
  templates_loader.py
  templates/
    verification_code.subject.txt
    verification_code.txt
    verification_code.html

darknight/services/config/models/email.py   # 多 accounts
darknight/db/models.py                      # EmailOutbox
darknight/db/migrations/versions/...        # 建表
darknight/config.yaml
darknight/utils/email_sender.py             # 薄封装或删除
darknight/api/v1/routers/auth.py            # 改调 mail.enqueue
```

实施顺序：

1. 扩展 `EmailConfig`（含旧字段兼容）。
2. 实现 MailService + 模板 + `email_outbox` 迁移。
3. `auth.send-code` 切换到新服务。
4. 清理旧单路径发送逻辑。

## 9. 验证计划

1. `dev_log_only=true`：发码产生日志 + outbox 记录。
2. 真实 SMTP：`noreply` 发出验证码（HTML + 纯文本可读）。
3. 错误密码：outbox → `failed`；send-code HTTP 仍返回成功（验证码已存）。
4. 未知 `account` / 缺模板：enqueue 快速失败并有明确日志。

## 10. 决议摘要

| 议题 | 决议 |
|------|------|
| 账号选用 | 按用途别名（`noreply` / `support`） |
| 能力范围 | 模板 + 进程内异步 + outbox 重试 |
| 队列 | FastAPI BackgroundTasks，无 Redis/Celery |
| 内容形态 | HTML + 纯文本双模板 |
| Outbox 正文 | 存渲染结果 |
| 与验证码表 | 两表分离，不合并 |
