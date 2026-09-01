<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { Trash2 } from 'lucide-vue-next'
import {
  ALPN_OPTIONS,
  FINGERPRINT_OPTIONS,
  HOST_SECURITY_OPTIONS,
  type HostEntry
} from '@/api/host/types'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from '@/components/ui/select'
import { Switch } from '@/components/ui/switch'

const host = defineModel<HostEntry>({ required: true })
defineEmits<{ remove: [] }>()
const { t } = useI18n()

/** Reka Select disallows empty-string item values; map default ↔ sentinel. */
const DEFAULT_SELECT = '__default__'

function toSelectValue(value: string) {
  return value === '' ? DEFAULT_SELECT : value
}

function fromSelectValue(value: string | number | bigint | Record<string, unknown> | null) {
  const s = String(value ?? '')
  return s === DEFAULT_SELECT ? '' : s
}

function onPortUpdate(value: string | number) {
  if (value === '' || value === null || value === undefined) {
    host.value.port = null
    return
  }
  const n = typeof value === 'number' ? value : Number(value)
  host.value.port = Number.isFinite(n) ? n : null
}
</script>

<template>
  <div class="rounded-xl border border-border bg-card p-4">
    <div class="mb-4 flex items-center gap-2">
      <Input v-model="host.remark" class="max-w-55" placeholder="Remark" />
      <div class="flex-1" />
      <div class="flex items-center gap-2">
        <span class="text-sm text-muted-foreground">{{ t('status.disabled') }}</span>
        <Switch
          :model-value="host.is_disabled"
          @update:model-value="(v: boolean) => (host.is_disabled = v)"
        />
      </div>
      <Button variant="ghost" size="icon" type="button" @click="$emit('remove')">
        <Trash2 class="size-4 text-destructive" />
      </Button>
    </div>

    <div class="space-y-4">
      <div class="grid gap-3 sm:grid-cols-2">
        <div class="space-y-2">
          <Label>{{ t('hostsDialog.currentServer') }}</Label>
          <Input v-model="host.address" />
        </div>
        <div class="space-y-2">
          <Label>{{ t('hostsDialog.port') }}</Label>
          <Input
            type="number"
            min="0"
            :model-value="host.port ?? ''"
            @update:model-value="onPortUpdate"
          />
        </div>
      </div>

      <div class="grid gap-3 sm:grid-cols-2">
        <div class="space-y-2">
          <Label>{{ t('hostsDialog.host') }}</Label>
          <Input
            :model-value="host.host ?? ''"
            @update:model-value="(v) => (host.host = String(v))"
          />
        </div>
        <div class="space-y-2">
          <Label>{{ t('hostsDialog.sni') }}</Label>
          <Input
            :model-value="host.sni ?? ''"
            @update:model-value="(v) => (host.sni = String(v))"
          />
        </div>
      </div>

      <div class="space-y-2">
        <Label>{{ t('hostsDialog.path') }}</Label>
        <Input
          :model-value="host.path ?? ''"
          @update:model-value="(v) => (host.path = String(v))"
        />
      </div>

      <div class="grid gap-3 sm:grid-cols-3">
        <div class="space-y-2">
          <Label>{{ t('hostsDialog.security') }}</Label>
          <Select
            :model-value="host.security"
            @update:model-value="(v) => (host.security = String(v))"
          >
            <SelectTrigger class="w-full">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem
                v-for="s in HOST_SECURITY_OPTIONS"
                :key="s.value"
                :value="s.value"
              >
                {{ s.title }}
              </SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div class="space-y-2">
          <Label>{{ t('hostsDialog.alpn') }}</Label>
          <Select
            :model-value="toSelectValue(host.alpn)"
            @update:model-value="(v) => (host.alpn = fromSelectValue(v))"
          >
            <SelectTrigger class="w-full">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem
                v-for="a in ALPN_OPTIONS"
                :key="toSelectValue(a)"
                :value="toSelectValue(a)"
              >
                {{ a || 'default' }}
              </SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div class="space-y-2">
          <Label>{{ t('hostsDialog.fingerprint') }}</Label>
          <Select
            :model-value="toSelectValue(host.fingerprint)"
            @update:model-value="(v) => (host.fingerprint = fromSelectValue(v))"
          >
            <SelectTrigger class="w-full">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem
                v-for="f in FINGERPRINT_OPTIONS"
                :key="toSelectValue(f)"
                :value="toSelectValue(f)"
              >
                {{ f || 'default' }}
              </SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <details class="rounded-lg border border-border p-3">
        <summary class="cursor-pointer text-sm font-medium text-foreground">
          {{ t('hostsDialog.advancedOptions') }}
        </summary>
        <div class="mt-3 space-y-4">
          <div class="space-y-2">
            <Label>{{ t('hostsDialog.fragment') }}</Label>
            <Input
              :model-value="String(host.fragment_setting ?? '')"
              :placeholder="String(t('hostsDialog.fragment.info'))"
              @update:model-value="(v) => (host.fragment_setting = String(v))"
            />
          </div>
          <div class="space-y-2">
            <Label>{{ t('hostsDialog.noise') }}</Label>
            <Input
              :model-value="String(host.noise_setting ?? '')"
              :placeholder="String(t('hostsDialog.noise.info'))"
              @update:model-value="(v) => (host.noise_setting = String(v))"
            />
          </div>
          <div class="flex flex-wrap gap-x-6 gap-y-3">
            <div class="flex items-center gap-2">
              <Switch
                :model-value="host.allowinsecure"
                @update:model-value="(v: boolean) => (host.allowinsecure = v)"
              />
              <span class="text-sm text-foreground">{{ t('hostsDialog.allowinsecure') }}</span>
            </div>
            <div class="flex items-center gap-2">
              <Switch
                :model-value="host.mux_enable"
                @update:model-value="(v: boolean) => (host.mux_enable = v)"
              />
              <span class="text-sm text-foreground">{{ t('hostsDialog.muxEnable') }}</span>
            </div>
            <div class="flex items-center gap-2">
              <Switch
                :model-value="host.random_user_agent"
                @update:model-value="(v: boolean) => (host.random_user_agent = v)"
              />
              <span class="text-sm text-foreground">{{ t('hostsDialog.randomUserAgent') }}</span>
            </div>
            <div class="flex items-center gap-2">
              <Switch
                :model-value="host.use_sni_as_host"
                @update:model-value="(v: boolean) => (host.use_sni_as_host = v)"
              />
              <span class="text-sm text-foreground">{{ t('hostsDialog.useSniAsHost') }}</span>
            </div>
          </div>
        </div>
      </details>
    </div>
  </div>
</template>
