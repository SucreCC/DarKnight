<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import { ChevronLeft, ChevronRight, Copy, Link, Pencil, QrCode, Trash2 } from 'lucide-vue-next'
import { formatBytes } from '@/utils/formatter'
import { relativeExpiry, isExpired } from '@/utils/formatTime'
import { STATUS_BADGE, type User } from '@/api/user/types'
import { absoluteSubscriptionUrl, isUnlimited, usagePercentage, usageTotalText } from '../helpers'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from '@/components/ui/select'

const props = defineProps<{
  users: User[]
  total: number
  loading: boolean
  page: number
  limit: number
}>()

const emit = defineEmits<{
  edit: [user: User]
  qr: [user: User]
  remove: [user: User]
  'update:page': [page: number]
  'update:limit': [limit: number]
}>()

const { t } = useI18n()

const PAGE_SIZES = [10, 20, 30, 50, 100]

function statusBadge(status: User['status']) {
  return STATUS_BADGE[status] ?? 'secondary'
}

function expiryText(user: User): string {
  if (!user.expire) return ''
  const rel = relativeExpiry(user.expire)
  if (!rel) return ''
  return isExpired(user.expire) ? t('expired', { time: rel }) : t('expires', { time: rel })
}

function usageBarPercent(user: User): number {
  if (isUnlimited(user.data_limit)) return 100
  return usagePercentage(user.used_traffic, user.data_limit)
}

function usageBarExceeded(user: User): boolean {
  return !isUnlimited(user.data_limit) && usagePercentage(user.used_traffic, user.data_limit) >= 100
}

async function copy(text: string, message: string) {
  try {
    await navigator.clipboard.writeText(text)
    toast.success(message)
  } catch {
    toast.error('Copy failed')
  }
}

function copySubLink(user: User) {
  copy(absoluteSubscriptionUrl(user.subscription_url), t('usersTable.copied'))
}

function copyConfigs(user: User) {
  copy(user.links.join('\r\n'), t('usersTable.copied'))
}

const totalPages = computed(() => Math.max(1, Math.ceil(props.total / props.limit) || 1))

function goPrev() {
  if (props.page > 1) emit('update:page', props.page - 1)
}

function goNext() {
  if (props.page < totalPages.value) emit('update:page', props.page + 1)
}

function onPageSizeChange(value: string | number | bigint | Record<string, unknown> | null) {
  const n = Number(value)
  if (Number.isFinite(n) && n > 0) emit('update:limit', n)
}
</script>

<template>
  <div class="space-y-4">
    <div class="overflow-x-auto rounded-xl border border-border bg-card">
      <div v-if="loading && !users.length" class="space-y-3 p-4">
        <Skeleton v-for="i in 5" :key="i" class="h-10 w-full" />
      </div>

      <div
        v-else-if="!users.length"
        class="flex flex-col items-center gap-3 px-4 py-10 text-center text-muted-foreground"
      >
        <p class="text-sm">{{ t('usersTable.noUser') }}</p>
      </div>

      <table v-else class="w-full min-w-[720px] text-sm">
        <thead class="border-b border-border text-muted-foreground">
          <tr>
            <th class="px-4 py-3 text-start font-medium">{{ t('username') }}</th>
            <th class="px-4 py-3 text-start font-medium">{{ t('usersTable.status') }}</th>
            <th class="px-4 py-3 text-start font-medium">{{ t('usersTable.dataUsage') }}</th>
            <th class="px-4 py-3 text-end font-medium" />
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="row in users"
            :key="row.username"
            class="cursor-pointer border-b border-border last:border-0 hover:bg-muted/40"
            @click="emit('edit', row)"
          >
            <td class="px-4 py-3">
              <div class="flex items-center gap-2">
                <span
                  class="size-2 shrink-0 rounded-full"
                  :class="row.online_at ? 'bg-emerald-500' : 'bg-muted-foreground/40'"
                />
                <span class="text-foreground">{{ row.username }}</span>
              </div>
            </td>
            <td class="px-4 py-3">
              <div class="flex flex-col gap-0.5">
                <Badge :variant="statusBadge(row.status)">
                  {{ t(`status.${row.status}`) }}
                </Badge>
                <span v-if="expiryText(row)" class="text-xs text-muted-foreground">
                  {{ expiryText(row) }}
                </span>
              </div>
            </td>
            <td class="px-4 py-3">
              <div class="min-w-[180px] space-y-1">
                <div class="h-1.5 overflow-hidden rounded-full bg-muted">
                  <div
                    class="h-full rounded-full transition-[width]"
                    :class="usageBarExceeded(row) ? 'bg-destructive' : 'bg-primary'"
                    :style="{ width: `${usageBarPercent(row)}%` }"
                  />
                </div>
                <div class="flex justify-between gap-2 text-xs text-muted-foreground">
                  <span>
                    {{ formatBytes(row.used_traffic) }} /
                    {{ usageTotalText(row.data_limit, row.data_limit_reset_strategy, t) }}
                  </span>
                  <span>
                    {{ t('usersTable.total') }}: {{ formatBytes(row.lifetime_used_traffic) }}
                  </span>
                </div>
              </div>
            </td>
            <td class="px-4 py-3 text-end" @click.stop>
              <div class="inline-flex items-center gap-1">
                <Button
                  variant="ghost"
                  size="icon"
                  type="button"
                  :title="t('usersTable.copyLink')"
                  @click="copySubLink(row)"
                >
                  <Link class="size-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  type="button"
                  :title="t('usersTable.copyConfigs')"
                  @click="copyConfigs(row)"
                >
                  <Copy class="size-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  type="button"
                  title="QR Code"
                  @click="emit('qr', row)"
                >
                  <QrCode class="size-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  type="button"
                  :title="t('userDialog.editUser')"
                  @click="emit('edit', row)"
                >
                  <Pencil class="size-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  type="button"
                  :title="t('delete')"
                  @click="emit('remove', row)"
                >
                  <Trash2 class="size-4 text-destructive" />
                </Button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="flex flex-wrap items-center justify-between gap-3">
      <p class="text-sm text-muted-foreground">
        {{ total }}
      </p>
      <div class="flex flex-wrap items-center gap-2">
        <Select :model-value="String(limit)" @update:model-value="onPageSizeChange">
          <SelectTrigger class="w-[100px]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem v-for="size in PAGE_SIZES" :key="size" :value="String(size)">
              {{ size }}
            </SelectItem>
          </SelectContent>
        </Select>
        <Button
          variant="outline"
          size="sm"
          type="button"
          :disabled="page <= 1"
          @click="goPrev"
        >
          <ChevronLeft class="size-4" />
          {{ t('previous') }}
        </Button>
        <span class="px-1 text-sm text-muted-foreground">
          {{ page }} / {{ totalPages }}
        </span>
        <Button
          variant="outline"
          size="sm"
          type="button"
          :disabled="page >= totalPages"
          @click="goNext"
        >
          {{ t('next') }}
          <ChevronRight class="size-4" />
        </Button>
      </div>
    </div>
  </div>
</template>
