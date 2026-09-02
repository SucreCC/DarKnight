# 工单系统实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 实现门户工单（列表/创建/详情/回复）与管理端工单管理（列表/筛选/处理）。

**Architecture:** 后端 `tickets` + `ticket_replies` 两表；门户与 Admin 共用 API router；前端对齐 Orders（门户）与 Product/User（Admin）模式。

**Tech Stack:** FastAPI, SQLAlchemy, Alembic, Vue 3, tanstack query, shadcn

## Global Constraints

- 工单等级四档：`low` / `normal` / `high` / `urgent`
- 状态四档：`open` / `pending` / `resolved` / `closed`
- 首版无附件、无通知、无指派
- UI 对齐项目 Tailwind + shadcn 风格

---

## 任务清单（已完成）

- [x] Task 1: 后端 ORM + migration + Pydantic + crud + router
- [x] Task 2: 门户 API 客户端 + 列表页 + 创建弹窗
- [x] Task 3: 门户详情页 + 回复
- [x] Task 4: Admin API + 列表 + 筛选 + 处理弹窗
- [x] Task 5: 路由、i18n、菜单图标

**Spec:** `docs/superpowers/specs/2026-09-02-ticket-system-design.md`
