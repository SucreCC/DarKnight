<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { useQuery } from '@tanstack/vue-query'
import { User, DataLine, Cpu } from '@element-plus/icons-vue'
import { http } from '@/config/axios'
import { formatBytes, numberWithCommas } from '@/utils/formatter'

type SystemStats = {
  version: string
  users_active: number
  total_user: number
  incoming_bandwidth: number
  outgoing_bandwidth: number
  mem_used: number
  mem_total: number
}

const { t } = useI18n()
const { data } = useQuery({
  queryKey: ['system'],
  queryFn: () => http<SystemStats>('/system'),
  refetchInterval: 5000
})
</script>

<template>
  <el-row :gutter="16" class="stats">
    <el-col :xs="24" :sm="8">
      <el-card shadow="never">
        <div class="stat">
          <el-icon class="stat-icon" :size="26"><User /></el-icon>
          <div>
            <div class="stat-title">{{ t('activeUsers') }}</div>
            <div class="stat-value">
              {{ data ? numberWithCommas(data.users_active) : '-' }}
              <span class="stat-sub">/ {{ data ? numberWithCommas(data.total_user) : '-' }}</span>
            </div>
          </div>
        </div>
      </el-card>
    </el-col>
    <el-col :xs="24" :sm="8">
      <el-card shadow="never">
        <div class="stat">
          <el-icon class="stat-icon" :size="26"><DataLine /></el-icon>
          <div>
            <div class="stat-title">{{ t('dataUsage') }}</div>
            <div class="stat-value">
              {{ data ? formatBytes(data.incoming_bandwidth + data.outgoing_bandwidth) : '-' }}
            </div>
          </div>
        </div>
      </el-card>
    </el-col>
    <el-col :xs="24" :sm="8">
      <el-card shadow="never">
        <div class="stat">
          <el-icon class="stat-icon" :size="26"><Cpu /></el-icon>
          <div>
            <div class="stat-title">{{ t('memoryUsage') }}</div>
            <div class="stat-value">
              {{ data ? formatBytes(data.mem_used, 1) : '-' }}
              <span class="stat-sub">/ {{ data ? formatBytes(data.mem_total, 1) : '-' }}</span>
            </div>
          </div>
        </div>
      </el-card>
    </el-col>
  </el-row>
</template>

<style scoped>
.stats {
  margin-bottom: 16px;
}

.stat {
  display: flex;
  align-items: center;
  gap: 14px;
}

.stat-icon {
  color: var(--el-color-primary);
}

.stat-title {
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
}

.stat-sub {
  font-size: 14px;
  font-weight: 400;
  color: var(--el-text-color-secondary);
}
</style>
