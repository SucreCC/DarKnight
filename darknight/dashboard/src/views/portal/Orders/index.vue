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
import { currencySymbol, formatPrice } from '../Buy/plans'
import { usePlanCatalog } from '../Buy/usePlanCatalog'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'

const { t } = useI18n()
const router = useRouter()

const STATUS_VARIANT: Record<
  OrderStatus,
  'secondary' | 'default' | 'outline' | 'destructive'
> = {
  pending: 'secondary',
  paid: 'default',
  closed: 'outline',
  failed: 'destructive'
}

const { data, isLoading, isError } = useQuery({
  queryKey: ['portal', 'orders'],
  queryFn: fetchPortalOrders,
  refetchOnWindowFocus: false
})

const { getPlan } = usePlanCatalog()

function planName(order: PortalOrder) {
  return getPlan(order.plan_id)?.name ?? order.plan_id
}

function openOrder(order: PortalOrder) {
  router.push({ name: 'portal-order-detail', params: { orderId: order.id } })
}
</script>

<template>
  <div class="max-w-6xl">
    <Alert v-if="isError" variant="destructive" class="mb-4">
      <AlertDescription>{{ t('portal.requestFailed') }}</AlertDescription>
    </Alert>

    <div class="overflow-x-auto rounded-xl border border-border bg-card">
      <div v-if="isLoading" class="space-y-3 p-4">
        <Skeleton v-for="i in 5" :key="i" class="h-10 w-full" />
      </div>

      <div
        v-else-if="!(data ?? []).length"
        class="flex flex-col items-center gap-3 py-10 text-muted-foreground"
      >
        <p>{{ t('portal.orders.empty') }}</p>
        <Button @click="router.push({ name: 'portal-buy' })">
          {{ t('portal.buy.subscribeNow') }}
        </Button>
      </div>

      <table v-else class="w-full min-w-[720px] text-sm">
        <thead class="border-b border-border text-muted-foreground">
          <tr>
            <th class="px-4 py-3 text-start font-medium">{{ t('portal.buy.orderNo') }}</th>
            <th class="px-4 py-3 text-start font-medium">{{ t('portal.buy.productInfo') }}</th>
            <th class="px-4 py-3 text-start font-medium">{{ t('portal.buy.orderTotal') }}</th>
            <th class="px-4 py-3 text-start font-medium">{{ t('portal.orders.status') }}</th>
            <th class="px-4 py-3 text-start font-medium">{{ t('portal.buy.createdAt') }}</th>
            <th class="px-4 py-3 text-end font-medium">{{ t('portal.orders.action') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="row in data"
            :key="row.id"
            class="border-b border-border last:border-0"
          >
            <td class="px-4 py-3">
              <button
                type="button"
                class="text-primary hover:underline"
                @click="openOrder(row)"
              >
                {{ row.id }}
              </button>
            </td>
            <td class="px-4 py-3">{{ planName(row) }}</td>
            <td class="px-4 py-3">
              {{ currencySymbol(row.currency) }}{{ formatPrice(row.amount) }}
            </td>
            <td class="px-4 py-3">
              <Badge :variant="STATUS_VARIANT[row.status]">
                {{ t(`portal.orders.status.${row.status}`) }}
              </Badge>
            </td>
            <td class="px-4 py-3 text-muted-foreground">
              {{ formatOrderTime(row.created_at) }}
            </td>
            <td class="px-4 py-3 text-end">
              <Button
                size="sm"
                :variant="row.status === 'pending' ? 'default' : 'outline'"
                @click="openOrder(row)"
              >
                {{
                  row.status === 'pending'
                    ? t('portal.buy.checkout')
                    : t('portal.orders.detail')
                }}
              </Button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
