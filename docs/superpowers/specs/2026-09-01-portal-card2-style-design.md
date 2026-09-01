# 门户图二气质试验（壳 + 仪表盘）

日期：2026-09-01  
分支：`feat/portal-card2-style`  
状态：试验实现中  

## 目标

贴近参考图二（浅冷灰底、统一大圆角白卡、轻阴影工作台），**主色仍用现有紫**；不做步骤条/识图双栏。

## 改动

- `UserLayout`：主区 `bg-slate-100`；侧栏白底；菜单 `rounded-xl`；内容区 padding 加大  
- `Dashboard`：四卡 `rounded-2xl` + 统一边框/阴影；公告去左边线；流量条略粗；复制按钮用实心 primary；捷径 hover 浅灰、图标偏 primary  

## 非目标

Buy / 登录 / Admin；换成科技蓝主色。
