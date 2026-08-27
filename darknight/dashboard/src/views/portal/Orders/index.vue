<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { useQuery } from '@tanstack/vue-query'
import {
  fetchPortalOrders,
  formatOrderTime,
  type OrderStatus,
  type PortalOrder
} from '@/api/portal/orders'
import { currencySymbol, formatPrice, getCycleLabelKey, getPlanMeta } from '../Buy/plans'

const { t } = useI18n()
const router = useRouter()

const STATUS_TAG: Record<OrderStatus, 'warning' | 'success' | 'info' | 'danger'> = {
  pending: 'warning',
  paid: 'success',
  closed: 'info',
  failed: 'danger'
}

const { data, isLoading, isError } = useQuery({
  queryKey: ['portal', 'orders'],
  queryFn: fetchPortalOrders,
  refetchOnWindowFocus: false
})

const asOrder = (row: unknown) => row as PortalOrder

function planName(order: PortalOrder) {
  return getPlanMeta(order.plan_id)?.name ?? order.plan_id
}

function openOrder(order: PortalOrder) {
  router.push({ name: 'portal-order-detail', params: { orderId: order.id } })
}
</script>

<template>
  <div class="orders-page">
    <el-alert
      v-if="isError"
      type="error"
      :title="t('portal.requestFailed')"
      show-icon
      :closable="false"
      class="orders-alert"
    />

    <el-table v-loading="isLoading" :data="data ?? []" class="orders-table">
      <el-table-column :label="t('portal.buy.orderNo')" min-width="200">
        <template #default="{ row }">
          <el-link type="primary" @click="openOrder(asOrder(row))">{{ row.id }}</el-link>
        </template>
      </el-table-column>
      <el-table-column :label="t('portal.buy.productInfo')" min-width="140">
        <template #default="{ row }">
          {{ planName(asOrder(row)) }} · {{ t(getCycleLabelKey(row.cycle_id)) }}
        </template>
      </el-table-column>
      <el-table-column :label="t('portal.buy.orderTotal')" min-width="120">
        <template #default="{ row }">
          {{ currencySymbol(row.currency) }}{{ formatPrice(row.amount) }}
        </template>
      </el-table-column>
      <el-table-column :label="t('portal.orders.status')" min-width="110">
        <template #default="{ row }">
          <el-tag :type="STATUS_TAG[row.status as OrderStatus]" disable-transitions>
            {{ t(`portal.orders.status.${row.status}`) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column :label="t('portal.buy.createdAt')" min-width="180">
        <template #default="{ row }">{{ formatOrderTime(row.created_at) }}</template>
      </el-table-column>
      <el-table-column :label="t('portal.orders.action')" width="120" align="right">
        <template #default="{ row }">
          <el-button
            v-if="row.status === 'pending'"
            size="small"
            type="primary"
            @click="openOrder(asOrder(row))"
          >
            {{ t('portal.buy.checkout') }}
          </el-button>
          <el-button v-else size="small" @click="openOrder(asOrder(row))">
            {{ t('portal.orders.detail') }}
          </el-button>
        </template>
      </el-table-column>
      <template #empty>
        <div class="orders-empty">
          <p>{{ t('portal.orders.empty') }}</p>
          <el-button type="primary" @click="router.push({ name: 'portal-buy' })">
            {{ t('portal.buy.subscribeNow') }}
          </el-button>
        </div>
      </template>
    </el-table>
  </div>
</template>

<style scoped>
.orders-page {
  max-width: 1200px;
}

.orders-alert {
  margin-bottom: 16px;
}

.orders-table {
  background: #fff;
  border-radius: 8px;
}

.orders-empty {
  padding: 24px 0;
  color: #909399;
}

.orders-empty p {
  margin: 0 0 12px;
}
</style>
