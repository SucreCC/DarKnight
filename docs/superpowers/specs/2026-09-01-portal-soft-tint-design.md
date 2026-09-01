# 门户柔和色块减白设计

日期：2026-09-01  
状态：已确认，直接实现  

## 决策

- 调性：柔和色块（公告/流量淡紫 tint；订阅/捷径白卡）
- 范围：`UserLayout` + 仪表盘；不改 Buy/Admin
- 主区加深底色；侧栏极浅紫灰；顶栏白底加强边线

## 实现要点

1. `UserLayout`：主区 `bg-muted`；侧栏 `bg-primary/[0.03]`；顶栏保留 `bg-card` + `border-border`
2. Dashboard 公告：`bg-primary/5 border-primary/15`
3. Dashboard 流量：可选 `bg-primary/[0.03]` + primary 小图标
4. 订阅/捷径：`bg-card shadow-sm`
5. 仅用 token / 透明度，不写死青绿；暗色靠同一套 `/` 透明度

## 非目标

- 全站其它页同步、新色板、暗色专项重设计
