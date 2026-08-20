<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import * as ElIcons from '@element-plus/icons-vue'
import type { Component } from 'vue'
import { portalRoutes } from '@/router/portal'
import { fetchPortalMe } from '@/api/portal'
import type { PortalUser } from '@/api/portal/types'
import { removeUserToken } from '@/utils/userAuth'
import LanguageSwitch from '@/components/LanguageSwitch/index.vue'
import { getDocById } from '@/views/portal/Docs/articles'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()

const user = ref<PortalUser | null>(null)
const iconMap = ElIcons as unknown as Record<string, Component>

const menuChildren = computed(() => {
  const portalRoot = portalRoutes.find((r) => r.path === '/portal')
  return portalRoot?.children ?? []
})

interface MenuGroup {
  label?: string
  items: typeof menuChildren.value
}

const menuGroups = computed<MenuGroup[]>(() => {
  const groups: MenuGroup[] = []
  let current: MenuGroup = { items: [] }

  for (const item of menuChildren.value) {
    if (item.meta?.hideInMenu) continue
    const group = item.meta?.group as string | undefined
    if (group) {
      if (current.label !== group) {
        if (current.items.length) groups.push(current)
        current = { label: group, items: [] }
      }
      current.items.push(item)
    } else {
      if (current.label) {
        groups.push(current)
        current = { items: [] }
      }
      current.items.push(item)
    }
  }
  if (current.items.length) groups.push(current)
  return groups
})

const activeMenu = computed(() => {
  if (String(route.name).startsWith('portal-docs')) return 'portal-docs'
  if (String(route.name).startsWith('portal-buy')) return 'portal-buy'
  if (String(route.name).startsWith('portal-order')) return 'portal-orders'
  return route.name as string
})

const pageTitle = computed(() => {
  if (route.name === 'portal-docs-detail') {
    const article = getDocById(String(route.params.id || ''))
    if (article) {
      return t('portal.docs.headerTitle', {
        title: t(article.titleKey),
        date: article.updatedAt
      })
    }
  }
  if (route.name === 'portal-buy-configure') {
    return t('portal.buy.configureTitle')
  }
  if (route.name === 'portal-order-detail') {
    return t('portal.buy.orderDetailTitle')
  }
  const current = menuChildren.value.find((item) => item.name === route.name)
  return current?.meta?.title ? t(current.meta.title as string) : t('portal.menu.dashboard')
})

onMounted(async () => {
  try {
    user.value = await fetchPortalMe()
  } catch {
    /* 401 handled by axios */
  }
})

function onSelect(index: string) {
  router.push({ name: index })
}

function logout() {
  removeUserToken()
  router.push({ name: 'site-home' })
}
</script>

<template>
  <div class="user-layout">
    <header class="user-header">
      <div class="user-header-left">{{ t('portal.siteName') }}</div>
      <div class="user-header-center">{{ pageTitle }}</div>
      <div class="user-header-right">
        <LanguageSwitch />
        <el-dropdown>
          <span class="user-profile">
            <el-icon><component :is="iconMap.User" /></el-icon>
            {{ user?.email || '...' }}
            <el-icon><component :is="iconMap.ArrowDown" /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="logout">{{ t('portal.logout') }}</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </header>
    <div class="user-body">
      <aside class="user-aside">
        <el-menu :default-active="activeMenu" @select="onSelect">
          <template v-for="(group, gi) in menuGroups" :key="gi">
            <div v-if="group.label" class="menu-group-label">{{ t(group.label) }}</div>
            <el-menu-item
              v-for="item in group.items"
              :key="item.name as string"
              :index="item.name as string"
            >
              <el-icon>
                <component :is="iconMap[item.meta!.icon as string]" />
              </el-icon>
              <span>{{ t(item.meta!.title as string) }}</span>
            </el-menu-item>
          </template>
        </el-menu>
      </aside>
      <main class="user-main">
        <router-view />
      </main>
    </div>
  </div>
</template>

<style scoped>
.user-layout {
  display: flex;
  min-height: 100vh;
  flex-direction: column;
  background: #eef2f6;
}

.user-header {
  display: grid;
  height: 56px;
  padding: 0 20px;
  color: #fff;
  background: #20a397;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
}

.user-header-left {
  font-size: 18px;
  font-weight: 700;
}

.user-header-center {
  font-size: 16px;
  font-weight: 500;
}

.user-header-right {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 16px;
}

.user-profile {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: #fff;
  cursor: pointer;
}

.user-body {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.user-aside {
  width: 220px;
  overflow: auto;
  background: #f5f7fa;
  border-right: 1px solid #e4e7ed;
}

.menu-group-label {
  padding: 16px 20px 8px;
  font-size: 12px;
  color: #909399;
}

.user-main {
  flex: 1;
  padding: 20px;
  overflow: auto;
}

.el-menu {
  border-right: none;
  background: transparent;
}
</style>
