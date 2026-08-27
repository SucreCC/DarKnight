<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { Check } from '@element-plus/icons-vue'
import { currencySymbol, formatPrice, type PlanFilter } from './plans'
import { usePlanCatalog, type PricedPlan } from './usePlanCatalog'

const { t } = useI18n()
const router = useRouter()

const activeFilter = ref<PlanFilter>('all')
const { currency, filterPlans, isLoading, isError } = usePlanCatalog()

const filters: { id: PlanFilter; labelKey: string }[] = [
  { id: 'all', labelKey: 'portal.buy.filter.all' },
  { id: 'period', labelKey: 'portal.buy.filter.period' },
  { id: 'traffic', labelKey: 'portal.buy.filter.traffic' }
]

const plans = computed(() => filterPlans(activeFilter.value))

function displayCycle(plan: PricedPlan) {
  return plan.cycles.find((cycle) => cycle.id === plan.displayCycleId) ?? plan.cycles[0]
}

function subscribe(planId: string) {
  router.push({ name: 'portal-buy-configure', params: { planId } })
}
</script>

<template>
  <div class="buy-page">
    <h2 class="buy-title">{{ t('portal.buy.choosePlan') }}</h2>

    <div class="buy-filters">
      <button
        v-for="item in filters"
        :key="item.id"
        type="button"
        class="filter-btn"
        :class="{ active: activeFilter === item.id }"
        @click="activeFilter = item.id"
      >
        {{ t(item.labelKey) }}
      </button>
    </div>

    <el-alert
      v-if="isError"
      type="error"
      :title="t('portal.buy.plansLoadFailed')"
      show-icon
      :closable="false"
      class="plans-alert"
    />

    <div v-loading="isLoading" class="plan-grid">
      <el-card v-for="plan in plans" :key="plan.id" shadow="never" class="plan-card">
        <div class="plan-name">{{ plan.name }}</div>
        <div class="plan-price">
          <span class="currency">{{ currencySymbol(currency) }}</span>
          <span class="amount">{{ formatPrice(displayCycle(plan).price) }}</span>
          <span class="cycle">{{ t(displayCycle(plan).labelKey) }}</span>
        </div>
        <ul class="plan-features">
          <li v-for="key in plan.featureKeys" :key="key">
            <el-icon class="check-icon"><Check /></el-icon>
            <span>{{ t(key) }}</span>
          </li>
        </ul>
        <el-button type="primary" class="subscribe-btn" @click="subscribe(plan.id)">
          {{ t('portal.buy.subscribeNow') }}
        </el-button>
      </el-card>
    </div>
  </div>
</template>

<style scoped>
.buy-page {
  max-width: 1200px;
}

.buy-title {
  margin: 0 0 20px;
  font-size: 22px;
  font-weight: 700;
  color: #303133;
}

.plans-alert {
  margin-bottom: 16px;
}

.buy-filters {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
}

.filter-btn {
  padding: 8px 18px;
  font-size: 14px;
  color: #606266;
  cursor: pointer;
  background: #fff;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
}

.filter-btn.active {
  color: #fff;
  background: #20a397;
  border-color: #20a397;
}

.plan-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 20px;
  align-items: stretch;
}

.plan-card {
  display: flex;
  height: 100%;
  flex-direction: column;
}

.plan-card :deep(.el-card__body) {
  display: flex;
  flex: 1;
  flex-direction: column;
  height: 100%;
}

.plan-name {
  margin-bottom: 12px;
  font-size: 28px;
  font-weight: 700;
  color: #303133;
}

.plan-price {
  display: flex;
  margin-bottom: 20px;
  align-items: baseline;
  gap: 4px;
}

.currency {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.amount {
  font-size: 36px;
  font-weight: 700;
  line-height: 1;
  color: #303133;
}

.cycle {
  font-size: 14px;
  color: #909399;
}

.plan-features {
  padding: 0;
  margin: 0;
  list-style: none;
  flex: 1;
}

.plan-features li {
  display: flex;
  padding: 6px 0;
  font-size: 14px;
  line-height: 1.5;
  color: #606266;
  align-items: flex-start;
  gap: 8px;
}

.check-icon {
  margin-top: 3px;
  color: #20a397;
  flex-shrink: 0;
}

.subscribe-btn {
  width: 100%;
  height: 44px;
  margin-top: 24px;
  background: #20a397;
  border-color: #20a397;
  flex-shrink: 0;
}

.subscribe-btn:hover,
.subscribe-btn:focus {
  background: #1b8c82;
  border-color: #1b8c82;
}

@media (width <= 1100px) {
  .plan-grid {
    grid-template-columns: 1fr;
  }
}
</style>
