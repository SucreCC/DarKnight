<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import {
  Expand,
  Fold,
  Setting as SettingIcon,
  SwitchButton,
  User as UserIcon
} from '@element-plus/icons-vue'
import { http } from '@/config/axios'
import { removeToken } from '@/utils/auth'
import { useAppStore } from '@/store/modules/app'
import { useTagsViewStore } from '@/store/modules/tagsView'
import ThemeToggle from '@/components/ThemeToggle/index.vue'
import LanguageSwitch from '@/components/LanguageSwitch/index.vue'
import Breadcrumb from '../Breadcrumb/index.vue'

const emit = defineEmits<{ 'open-setting': [] }>()

const { t } = useI18n()
const router = useRouter()
const appStore = useAppStore()
const tagsViewStore = useTagsViewStore()

const adminName = ref('')

onMounted(async () => {
  try {
    const admin = await http<{ username: string }>('/admin')
    adminName.value = admin.username
  } catch {
    /* 401 由 axios 拦截器处理 */
  }
})

function logout() {
  removeToken()
  tagsViewStore.reset()
  router.push({ name: 'login' })
}
</script>

<template>
  <div class="layout-header">
    <el-button
      circle
      text
      :title="t('layout.toggleSidebar')"
      :aria-label="t('layout.toggleSidebar')"
      @click="appStore.toggleCollapsed()"
    >
      <el-icon :size="18">
        <Expand v-if="appStore.collapsed" />
        <Fold v-else />
      </el-icon>
    </el-button>
    <Breadcrumb v-if="appStore.showBreadcrumb" />
    <div class="dk-spacer" />
    <LanguageSwitch />
    <ThemeToggle />
    <el-button
      circle
      text
      :title="t('layout.settings')"
      :aria-label="t('layout.settings')"
      @click="emit('open-setting')"
    >
      <el-icon :size="18"><SettingIcon /></el-icon>
    </el-button>
    <el-dropdown>
      <span class="admin-name">
        <el-icon><UserIcon /></el-icon>
        {{ adminName || 'admin' }}
      </span>
      <template #dropdown>
        <el-dropdown-menu>
          <el-dropdown-item @click="logout">
            <el-icon><SwitchButton /></el-icon>
            {{ t('header.logout') }}
          </el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>
  </div>
</template>

<style scoped>
.layout-header {
  display: flex;
  align-items: center;
  height: 56px;
  padding: 0 16px;
  border-bottom: 1px solid var(--el-border-color);
  gap: 12px;
  flex-shrink: 0;
  background: var(--el-bg-color);
}

.admin-name {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  outline: none;
}
</style>
