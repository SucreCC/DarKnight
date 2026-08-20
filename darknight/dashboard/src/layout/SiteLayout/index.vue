<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import LanguageSwitch from '@/components/LanguageSwitch/index.vue'

const { t } = useI18n()
const router = useRouter()
</script>

<template>
  <div class="site-layout">
    <header class="site-header">
      <div class="site-header-inner">
        <button type="button" class="site-brand" @click="router.push({ name: 'site-home' })">
          <img src="/statics/logo.png" class="site-logo" alt="DarKnight" />
          <span>DarKnight</span>
        </button>
        <div class="site-actions">
          <LanguageSwitch />
          <el-button @click="router.push({ name: 'login' })">{{ t('portal.login') }}</el-button>
          <el-button type="primary" @click="router.push({ name: 'portal-register' })">
            {{ t('portal.register') }}
          </el-button>
        </div>
      </div>
    </header>
    <main class="site-main">
      <router-view />
    </main>
    <footer class="site-footer">
      <span>{{ t('site.footer') }}</span>
    </footer>
  </div>
</template>

<style scoped>
.site-layout {
  display: flex;
  min-height: 100vh;
  flex-direction: column;
  background: #f5f7fa;
}

.site-header {
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
}

.site-header-inner {
  display: flex;
  max-width: 1120px;
  height: 64px;
  padding: 0 24px;
  margin: 0 auto;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
}

.site-brand {
  display: inline-flex;
  padding: 0;
  font-size: 20px;
  font-weight: 700;
  color: #303133;
  cursor: pointer;
  background: transparent;
  border: none;
  align-items: center;
  gap: 10px;
}

.site-logo {
  width: 32px;
  height: 32px;
  object-fit: contain;
  border-radius: 8px;
}

.site-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.site-main {
  flex: 1;
  width: 100%;
  max-width: 1120px;
  padding: 32px 24px;
  margin: 0 auto;
}

.site-footer {
  padding: 20px 24px;
  font-size: 13px;
  color: #909399;
  text-align: center;
  border-top: 1px solid #e4e7ed;
  background: #fff;
}
</style>
