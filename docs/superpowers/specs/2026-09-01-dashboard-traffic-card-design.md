# 仪表盘流量使用卡设计

日期：2026-09-01  
状态：已确认，待写实现计划  

## 背景

门户仪表盘订阅卡内仅有一行文字展示 `used_traffic` / `data_limit`，不够醒目。用户希望用独立流量卡展示用量；后端暂无按日历史接口。

## 已确认决策

| 项 | 决策 |
|---|---|
| 形态 | 独立「流量使用」白卡片（方案 B） |
| 位置 | 公告下方、订阅/快捷入口上方，单独全宽一行（方案 A） |
| 视觉 | 进度条主视觉：标题 + 百分比 + 进度条 + 已用/总量与剩余 |
| 数据 | 仅用现有 `fetchPortalMe` 字段，不改后端 |
| 无订阅 | 不展示流量卡（避免空态噪音；用户走订阅卡虚线 CTA） |

## 一、布局

仪表盘自上而下：

1. 公告卡（不变）  
2. **流量使用卡**（有 `subscription_url` 时渲染）  
3. 订阅卡 | 快捷入口（双列）  

订阅卡内**删除**纯文字流量行；保留状态与订阅链接复制。

## 二、流量卡内容

容器：`rounded-xl border border-border bg-card p-5`，与现有门户卡一致。

### 有限额（`data_limit` 非 null 且 ≠ 0）

- 顶行：左侧标题；右侧百分比整数（如 `42%`）  
- 进度条：高约 8–10px，圆角；轨道 `bg-muted`；填充默认 `bg-primary`  
- 底行：左侧 `formatBytes(used) / formatBytes(limit)`；右侧「剩余 `formatBytes(remaining)`」  
- 计算：  
  - `percent = min(100, round(used / limit * 100))`  
  - `remaining = max(0, limit - used)`  

### 阈值色

| 条件 | 进度条填充与百分比 |
|------|-------------------|
| `< 80%` | `primary` |
| `≥ 80%` 且 `< 100%` | 警告色（如 amber） |
| `≥ 100%` | `destructive` |

### 无限额（`data_limit === null` 或 `0`）

- 不显示进度条  
- 显示已用字节 + Badge「不限」  
- 与 Admin `isUnlimited` 语义对齐（0 与 null 均视为不限）

### 无订阅

- 整卡不渲染  

## 三、实现要点

- 修改：`src/views/portal/Dashboard/index.vue`  
- 可抽极小本地计算（百分比/剩余/色阶），不必新建 store  
- i18n 新增键（`zh`/`en`/`ru`/`fa`），例如：  
  - `portal.dashboard.trafficUsage`（标题）  
  - `portal.dashboard.trafficRemaining`（剩余）  
  - `portal.dashboard.trafficUnlimited`（不限）  
  - 已有 `portal.dashboard.traffic` 可复用于「已用」语境或改为「已用 / 总量」组合文案  

## 四、验收

- 有订阅且有限额：见进度条、百分比、剩余；80%/100% 变色正确  
- 有订阅且不限：见已用 +「不限」，无进度条  
- 无订阅：无流量卡  
- 订阅卡不再重复文字流量行  
- 不新增 API  

## 五、非目标

- 用量趋势图 / 按日统计  
- 门户「流量」占位页真实功能  
- 到期时间卡（除非后续单独立项）  
