<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useI18n } from "vue-i18n";
import {
  Connection,
  Setting,
  SwitchButton,
  Link as LinkIcon,
  User as UserIcon,
} from "@element-plus/icons-vue";
import { http } from "@/shared/api/http";
import { removeAuthToken } from "@/shared/lib/authStorage";
import ThemeToggle from "@/components/ThemeToggle.vue";
import LanguageSwitch from "@/components/LanguageSwitch.vue";

const { t } = useI18n();
const route = useRoute();
const router = useRouter();

const adminName = ref("");
const activeMenu = computed(() => route.name as string);

onMounted(async () => {
  try {
    const admin = await http<{ username: string }>("/admin");
    adminName.value = admin.username;
  } catch {
    /* http interceptor handles 401 */
  }
});

function onSelect(index: string) {
  router.push({ name: index });
}

function logout() {
  removeAuthToken();
  router.push({ name: "login" });
}
</script>

<template>
  <el-container class="layout">
    <el-aside width="220px" class="layout-aside">
      <div class="layout-brand">DarKnight</div>
      <el-menu :default-active="activeMenu" @select="onSelect">
        <el-menu-item index="users">
          <el-icon><UserIcon /></el-icon>
          <span>{{ t("users") }}</span>
        </el-menu-item>
        <el-menu-item index="nodes">
          <el-icon><Connection /></el-icon>
          <span>{{ t("header.nodeSettings") }}</span>
        </el-menu-item>
        <el-menu-item index="hosts">
          <el-icon><LinkIcon /></el-icon>
          <span>{{ t("header.hostSettings") }}</span>
        </el-menu-item>
        <el-menu-item index="settings">
          <el-icon><Setting /></el-icon>
          <span>{{ t("core.title") }}</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="layout-header">
        <div class="dk-spacer" />
        <LanguageSwitch />
        <ThemeToggle />
        <el-dropdown>
          <span class="admin-name">
            <el-icon><UserIcon /></el-icon>
            {{ adminName || "admin" }}
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="logout">
                <el-icon><SwitchButton /></el-icon>
                {{ t("header.logout") }}
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
.layout {
  height: 100vh;
}
.layout-aside {
  border-right: 1px solid var(--el-border-color);
  display: flex;
  flex-direction: column;
}
.layout-aside :deep(.el-menu) {
  border-right: none;
}
.layout-brand {
  font-size: 20px;
  font-weight: 700;
  padding: 18px 20px;
}
.layout-header {
  display: flex;
  align-items: center;
  gap: 12px;
  border-bottom: 1px solid var(--el-border-color);
}
.admin-name {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  outline: none;
}
</style>
