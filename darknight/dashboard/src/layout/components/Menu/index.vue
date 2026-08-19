<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import * as ElIcons from '@element-plus/icons-vue'
import type { Component } from 'vue'
import { routes } from '@/router'
import { useAppStore } from '@/store/modules/app'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const appStore = useAppStore()

/** 菜单项来自路由表 children，避免菜单与路由两处维护 */
const menuItems = computed(() => {
  const root = routes.find((r) => r.path === '/')
  return (root?.children ?? []).filter((child) => child.meta?.title)
})

const activeMenu = computed(() => route.name as string)

const iconMap = ElIcons as unknown as Record<string, Component>

function onSelect(index: string) {
  router.push({ name: index })
}
</script>

<template>
  <div class="layout-brand">
    <img src="/statics/logo.png" class="brand-logo" alt="DarKnight" />
    <span v-show="!appStore.collapsed" class="brand-text">DarKnight</span>
  </div>
  <el-menu :default-active="activeMenu" :collapse="appStore.collapsed" @select="onSelect">
    <el-menu-item v-for="item in menuItems" :key="item.name as string" :index="item.name as string">
      <el-icon>
        <component :is="iconMap[item.meta!.icon as string]" />
      </el-icon>
      <template #title>{{ t(item.meta!.title as string) }}</template>
    </el-menu-item>
  </el-menu>
</template>

<style scoped>
.layout-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  height: 60px;
  padding: 0 20px;
  overflow: hidden;
  white-space: nowrap;
}

.brand-logo {
  width: 32px;
  height: 32px;
  object-fit: contain;
  border-radius: 8px;
  flex-shrink: 0;
}

.brand-text {
  font-size: 20px;
  font-weight: 700;
}

.el-menu {
  width: 100%;
  border-right: none;
  flex: 1;
}
</style>
