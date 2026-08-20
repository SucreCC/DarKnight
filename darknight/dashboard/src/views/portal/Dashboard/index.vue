<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import {
  Connection,
  HelpFilled,
  Plus,
  Reading,
  ShoppingBag
} from '@element-plus/icons-vue'
import { fetchPortalMe } from '@/api/portal'
import type { PortalUser } from '@/api/portal/types'
import { formatBytes } from '@/utils/formatter'

const { t } = useI18n()
const router = useRouter()
const user = ref<PortalUser | null>(null)

const shortcuts = [
  {
    title: 'portal.dashboard.shortcutDocs',
    desc: 'portal.dashboard.shortcutDocsDesc',
    icon: Reading,
    route: 'site-docs'
  },
  {
    title: 'portal.dashboard.shortcutSubscribe',
    desc: 'portal.dashboard.shortcutSubscribeDesc',
    icon: Connection,
    action: 'copySub'
  },
  {
    title: 'portal.dashboard.shortcutBuy',
    desc: 'portal.dashboard.shortcutBuyDesc',
    icon: ShoppingBag,
    route: 'portal-buy'
  },
  {
    title: 'portal.dashboard.shortcutSupport',
    desc: 'portal.dashboard.shortcutSupportDesc',
    icon: HelpFilled,
    route: 'portal-tickets'
  }
]

onMounted(async () => {
  user.value = await fetchPortalMe()
})

async function copySubscription() {
  if (!user.value?.subscription_url) return
  await navigator.clipboard.writeText(user.value.subscription_url)
}

function onShortcut(item: (typeof shortcuts)[number]) {
  if (item.action === 'copySub') {
    copySubscription()
    return
  }
  if (item.route) router.push({ name: item.route })
}
</script>

<template>
  <div class="portal-dashboard">
    <el-alert
      v-if="false"
      type="warning"
      :title="t('portal.dashboard.unpaidOrder')"
      show-icon
      class="portal-alert"
    />

    <el-card class="announcement-card" shadow="never">
      <el-tag type="warning" size="small">{{ t('portal.dashboard.announcement') }}</el-tag>
      <p class="announcement-text">{{ t('portal.dashboard.announcementText') }}</p>
      <span class="announcement-date">2026-08-19</span>
    </el-card>

    <div class="dashboard-grid">
      <el-card shadow="never" class="subscription-card">
        <template #header>
          <span>{{ t('portal.dashboard.mySubscription') }}</span>
        </template>
        <div v-if="user?.subscription_url" class="subscription-info">
          <p>
            <strong>{{ t('portal.dashboard.status') }}:</strong>
            {{ user.status }}
          </p>
          <p>
            <strong>{{ t('portal.dashboard.traffic') }}:</strong>
            {{ formatBytes(user.used_traffic) }}
            <template v-if="user.data_limit"> / {{ formatBytes(user.data_limit) }}</template>
          </p>
          <el-input :model-value="user.subscription_url" readonly>
            <template #append>
              <el-button @click="copySubscription">{{ t('portal.dashboard.copy') }}</el-button>
            </template>
          </el-input>
        </div>
        <div v-else class="empty-subscription" @click="router.push({ name: 'portal-buy' })">
          <el-icon :size="48"><Plus /></el-icon>
          <span>{{ t('portal.dashboard.buySubscription') }}</span>
        </div>
      </el-card>

      <el-card shadow="never" class="shortcuts-card">
        <template #header>
          <span>{{ t('portal.dashboard.shortcuts') }}</span>
        </template>
        <div
          v-for="item in shortcuts"
          :key="item.title"
          class="shortcut-item"
          @click="onShortcut(item)"
        >
          <div>
            <div class="shortcut-title">{{ t(item.title) }}</div>
            <div class="shortcut-desc">{{ t(item.desc) }}</div>
          </div>
          <el-icon :size="22"><component :is="item.icon" /></el-icon>
        </div>
      </el-card>
    </div>
  </div>
</template>

<style scoped>
.portal-dashboard {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.portal-alert {
  margin-bottom: 0;
}

.announcement-card {
  color: #fff;
  background: linear-gradient(135deg, #2c3e50, #4ca1af);
}

.announcement-text {
  margin: 12px 0 8px;
  font-size: 15px;
}

.announcement-date {
  font-size: 12px;
  opacity: 0.8;
}

.dashboard-grid {
  display: grid;
  gap: 16px;
  grid-template-columns: 1fr 1fr;
}

@media (width <= 960px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
}

.empty-subscription {
  display: flex;
  min-height: 180px;
  color: #909399;
  cursor: pointer;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.shortcut-item {
  display: flex;
  padding: 14px 0;
  cursor: pointer;
  border-bottom: 1px solid #ebeef5;
  justify-content: space-between;
  align-items: center;
}

.shortcut-item:last-child {
  border-bottom: none;
}

.shortcut-title {
  font-weight: 600;
}

.shortcut-desc {
  margin-top: 4px;
  font-size: 13px;
  color: #909399;
}

.subscription-info p {
  margin: 0 0 12px;
}
</style>
