<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { CircleHelp, Inbox, Loader2, UserPlus } from 'lucide-vue-next'
import { toast } from 'vue-sonner'
import {
  fetchInviteCodes,
  fetchInvitePayouts,
  fetchInviteSummary,
  formatInviteTime,
  generateInviteCode
} from '@/api/portal/invite'
import { currencySymbol, formatPrice } from '../Buy/plans'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'

const { t } = useI18n()
const queryClient = useQueryClient()

const summaryQuery = useQuery({
  queryKey: ['portal', 'invite', 'summary'],
  queryFn: fetchInviteSummary,
  refetchOnWindowFocus: false
})

const codesQuery = useQuery({
  queryKey: ['portal', 'invite', 'codes'],
  queryFn: fetchInviteCodes,
  refetchOnWindowFocus: false
})

const payoutsQuery = useQuery({
  queryKey: ['portal', 'invite', 'payouts'],
  queryFn: fetchInvitePayouts,
  refetchOnWindowFocus: false
})

const generateMutation = useMutation({
  mutationFn: generateInviteCode,
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['portal', 'invite', 'codes'] })
    queryClient.invalidateQueries({ queryKey: ['portal', 'invite', 'summary'] })
    toast.success(t('portal.invite.codeGenerated'), { id: 'invite-generate' })
  },
  onError: () => {
    toast.error(t('portal.invite.generateFailed'), { id: 'invite-generate' })
  }
})

const summary = computed(() => summaryQuery.data.value)
const codes = computed(() => codesQuery.data.value ?? [])
const payouts = computed(() => payoutsQuery.data.value ?? [])
const hasInviteCode = computed(() => codes.value.length > 0)

const commissionRateLabel = computed(() => {
  const rate = summary.value?.commission_rate ?? 0.1
  return `${Math.round(rate * 100)}%`
})

const hasError = computed(
  () => summaryQuery.isError.value || codesQuery.isError.value || payoutsQuery.isError.value
)

function money(amount: number, currency = summary.value?.currency ?? 'USD') {
  return `${currencySymbol(currency)}${formatPrice(amount)}`
}

function onGenerateCode() {
  generateMutation.mutate()
}

async function copyInviteLink(row: { invite_url: string }) {
  await navigator.clipboard.writeText(row.invite_url)
  toast.success(t('portal.invite.linkCopied'), { id: 'invite-copy-link' })
}
</script>

<template>
  <div class="flex max-w-6xl flex-col gap-5">
    <Alert v-if="hasError" variant="destructive">
      <AlertDescription>{{ t('portal.requestFailed') }}</AlertDescription>
    </Alert>

    <!-- 可划转佣金 -->
    <div class="rounded-2xl border border-slate-200/80 bg-card p-6 shadow-sm dark:border-border">
      <div class="mb-4 flex items-start justify-between gap-3">
        <span class="text-sm text-muted-foreground">{{ t('portal.menu.invite') }}</span>
        <UserPlus class="size-5 text-muted-foreground/60" />
      </div>

      <template v-if="summaryQuery.isLoading.value">
        <Skeleton class="mb-2 h-10 w-40" />
        <Skeleton class="h-4 w-28" />
      </template>
      <template v-else>
        <div class="flex flex-wrap items-end gap-2">
          <span class="text-4xl font-semibold tracking-tight text-foreground">
            {{ formatPrice(summary?.balance ?? 0) }}
          </span>
          <span class="pb-1 text-sm text-muted-foreground">{{ summary?.currency ?? 'USD' }}</span>
        </div>
        <p class="mt-1 text-sm text-muted-foreground">{{ t('portal.invite.currentBalance') }}</p>
        <p class="mt-2 text-xs text-muted-foreground">{{ t('portal.invite.balanceHint') }}</p>
      </template>
    </div>

    <!-- 统计概览 -->
    <div class="rounded-2xl border border-slate-200/80 bg-card p-6 shadow-sm dark:border-border">
      <template v-if="summaryQuery.isLoading.value">
        <div class="space-y-4">
          <Skeleton v-for="i in 4" :key="i" class="h-5 w-full" />
        </div>
      </template>
      <dl v-else class="divide-y divide-border">
        <div class="flex items-center justify-between gap-4 py-3 first:pt-0 last:pb-0">
          <dt class="text-sm text-muted-foreground">{{ t('portal.invite.registeredUsers') }}</dt>
          <dd class="text-sm font-medium text-foreground">
            {{ summary?.registered_count ?? 0 }}
          </dd>
        </div>
        <div class="flex items-center justify-between gap-4 py-3">
          <dt class="text-sm text-muted-foreground">{{ t('portal.invite.commissionRate') }}</dt>
          <dd class="text-sm font-medium text-foreground">{{ commissionRateLabel }}</dd>
        </div>
        <div class="flex items-center justify-between gap-4 py-3">
          <dt class="flex items-center gap-1.5 text-sm text-muted-foreground">
            {{ t('portal.invite.pendingCommission') }}
            <CircleHelp
              class="size-3.5 shrink-0 opacity-60"
              :title="t('portal.invite.pendingCommissionHint')"
            />
          </dt>
          <dd class="text-sm font-medium text-foreground">
            {{ money(summary?.pending_commission ?? 0) }}
          </dd>
        </div>
        <div class="flex items-center justify-between gap-4 py-3">
          <dt class="text-sm text-muted-foreground">{{ t('portal.invite.totalCommission') }}</dt>
          <dd class="text-sm font-medium text-foreground">
            {{ money(summary?.total_commission ?? 0) }}
          </dd>
        </div>
      </dl>
    </div>

    <!-- 邀请码管理 -->
    <div class="overflow-hidden rounded-2xl border border-slate-200/80 bg-card shadow-sm dark:border-border">
      <div class="flex flex-wrap items-center justify-between gap-3 border-b border-border px-6 py-4">
        <h2 class="text-base font-semibold text-foreground">{{ t('portal.invite.codeManagement') }}</h2>
        <Button
          v-if="!hasInviteCode"
          size="sm"
          :disabled="generateMutation.isPending.value || codesQuery.isLoading.value"
          @click="onGenerateCode"
        >
          <Loader2 v-if="generateMutation.isPending.value" class="mr-1.5 size-4 animate-spin" />
          {{ t('portal.invite.generateCode') }}
        </Button>
      </div>

      <div v-if="codesQuery.isLoading.value" class="space-y-3 p-4">
        <Skeleton v-for="i in 3" :key="i" class="h-10 w-full" />
      </div>

      <div
        v-else-if="!codes.length"
        class="flex flex-col items-center gap-2 py-12 text-muted-foreground"
      >
        <Inbox class="size-10 opacity-40" />
        <p class="text-sm">{{ t('portal.invite.empty') }}</p>
      </div>

      <table v-else class="w-full text-sm">
        <thead class="border-b border-border text-muted-foreground">
          <tr>
            <th class="px-6 py-3 text-start font-medium">{{ t('portal.invite.code') }}</th>
            <th class="px-6 py-3 text-end font-medium">{{ t('portal.invite.createdAt') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="row in codes"
            :key="row.code"
            class="border-b border-border last:border-0"
          >
            <td class="px-6 py-3">
              <div class="flex flex-wrap items-center gap-3">
                <span class="font-mono text-foreground">{{ row.code }}</span>
                <button
                  type="button"
                  class="text-sm font-medium text-primary hover:underline"
                  @click="copyInviteLink(row)"
                >
                  {{ t('portal.invite.copyLink') }}
                </button>
              </div>
            </td>
            <td class="px-6 py-3 text-end text-muted-foreground">
              {{ formatInviteTime(row.created_at) }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 佣金发放记录 -->
    <div class="overflow-hidden rounded-2xl border border-slate-200/80 bg-card shadow-sm dark:border-border">
      <div class="border-b border-border px-6 py-4">
        <h2 class="text-base font-semibold text-foreground">{{ t('portal.invite.payoutHistory') }}</h2>
      </div>

      <div v-if="payoutsQuery.isLoading.value" class="space-y-3 p-4">
        <Skeleton v-for="i in 3" :key="i" class="h-10 w-full" />
      </div>

      <div
        v-else-if="!payouts.length"
        class="flex flex-col items-center gap-2 py-12 text-muted-foreground"
      >
        <Inbox class="size-10 opacity-40" />
        <p class="text-sm">{{ t('portal.invite.payoutEmpty') }}</p>
      </div>

      <table v-else class="w-full text-sm">
        <thead class="border-b border-border text-muted-foreground">
          <tr>
            <th class="px-6 py-3 text-start font-medium">{{ t('portal.invite.payoutTime') }}</th>
            <th class="px-6 py-3 text-end font-medium">{{ t('portal.invite.payoutAmount') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(row, index) in payouts"
            :key="`${row.paid_at}-${index}`"
            class="border-b border-border last:border-0"
          >
            <td class="px-6 py-3 text-muted-foreground">
              {{ formatInviteTime(row.paid_at) }}
            </td>
            <td class="px-6 py-3 text-end font-medium text-foreground">
              {{ money(row.amount, row.currency) }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
