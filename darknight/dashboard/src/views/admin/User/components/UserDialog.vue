<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { Loader2, RefreshCw } from 'lucide-vue-next'
import { toast } from 'vue-sonner'
import { extractErrorDetail } from '@/config/axios'
import { useInboundsQuery, useUserMutations } from '@/api/user'
import {
  RESET_STRATEGIES,
  type Inbounds,
  type ProxyKey,
  type User,
  type UserCreate
} from '@/api/user/types'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from '@/components/ui/select'

const props = defineProps<{
  modelValue: boolean
  user: User | null
}>()
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  resetUsage: [user: User]
  revokeSub: [user: User]
}>()

const { t } = useI18n()
const { data: inboundsData } = useInboundsQuery()
const { createUser, updateUser } = useUserMutations()

const GB = 1073741824
const DAY = 24 * 60 * 60
const ALL_PROTOCOLS: ProxyKey[] = ['vmess', 'vless', 'trojan', 'shadowsocks']
const SS_METHODS = [
  'aes-128-gcm',
  'aes-256-gcm',
  'chacha20-ietf-poly1305',
  'xchacha20-ietf-poly1305'
]
/** Reka Select disallows empty-string item values; map none ↔ sentinel. */
const FLOW_NONE = '__none__'
const VLESS_FLOWS = ['', 'xtls-rprx-vision']

const isEditing = computed(() => !!props.user)
const errorMsg = ref('')
const fieldErrors = reactive<Record<string, string>>({})

type FormModel = {
  username: string
  selected_proxies: ProxyKey[]
  proxies: {
    vmess: { id: string }
    vless: { id: string; flow: string }
    trojan: { password: string }
    shadowsocks: { password: string; method: string }
  }
  inbounds: Record<string, string[]>
  data_limit: number | null
  data_limit_reset_strategy: string
  status: 'active' | 'on_hold'
  expire: number | null
  on_hold_expire_duration: number | null
  note: string
}

function defaultModel(): FormModel {
  return {
    username: '',
    selected_proxies: [...ALL_PROTOCOLS],
    proxies: {
      vmess: { id: '' },
      vless: { id: '', flow: '' },
      trojan: { password: '' },
      shadowsocks: { password: '', method: 'chacha20-ietf-poly1305' }
    },
    inbounds: {},
    data_limit: null,
    data_limit_reset_strategy: 'no_reset',
    status: 'active',
    expire: null,
    on_hold_expire_duration: null,
    note: ''
  }
}

const form = reactive<FormModel>(defaultModel())

const inboundsByProtocol = computed<Inbounds>(() => inboundsData.value ?? {})

function tagsFor(protocol: string): string[] {
  return (inboundsByProtocol.value[protocol] ?? []).map((i) => i.tag)
}

function toFlowSelect(value: string) {
  return value === '' ? FLOW_NONE : value
}

function fromFlowSelect(value: string | number | bigint | Record<string, unknown> | null) {
  const s = String(value ?? '')
  return s === FLOW_NONE ? '' : s
}

function validate(): boolean {
  Object.keys(fieldErrors).forEach((key) => delete fieldErrors[key])
  let ok = true
  if (!form.username.trim()) {
    fieldErrors.username = t('login.fieldRequired')
    ok = false
  }
  if (!form.selected_proxies.length) {
    fieldErrors.selected_proxies = t('userDialog.selectOneProtocol')
    ok = false
  }
  return ok
}

function resetToDefault() {
  Object.assign(form, defaultModel())
  // default: select all inbound tags per protocol
  const inbounds: Record<string, string[]> = {}
  for (const protocol of Object.keys(inboundsByProtocol.value)) {
    inbounds[protocol] = tagsFor(protocol)
  }
  form.inbounds = inbounds
}

function loadUser(user: User) {
  Object.assign(form, defaultModel())
  form.username = user.username
  form.selected_proxies = Object.keys(user.proxies) as ProxyKey[]
  form.proxies.vmess.id = user.proxies.vmess?.id ?? ''
  form.proxies.vless.id = user.proxies.vless?.id ?? ''
  form.proxies.vless.flow = user.proxies.vless?.flow ?? ''
  form.proxies.trojan.password = user.proxies.trojan?.password ?? ''
  form.proxies.shadowsocks.password = user.proxies.shadowsocks?.password ?? ''
  form.proxies.shadowsocks.method = user.proxies.shadowsocks?.method ?? 'chacha20-ietf-poly1305'
  form.inbounds = { ...user.inbounds }
  form.data_limit = user.data_limit ? Number((user.data_limit / GB).toFixed(5)) : null
  form.data_limit_reset_strategy = user.data_limit_reset_strategy
  form.status = user.status === 'on_hold' ? 'on_hold' : 'active'
  form.expire = user.expire
  form.on_hold_expire_duration = user.on_hold_expire_duration
    ? Number(user.on_hold_expire_duration / DAY)
    : null
  form.note = user.note ?? ''
}

watch(
  () => props.modelValue,
  (open) => {
    errorMsg.value = ''
    Object.keys(fieldErrors).forEach((key) => delete fieldErrors[key])
    if (!open) return
    if (props.user) loadUser(props.user)
    else resetToDefault()
  }
)

const expireDateStr = computed({
  get: () => {
    if (!form.expire) return ''
    const d = new Date(form.expire * 1000)
    const y = d.getFullYear()
    const m = String(d.getMonth() + 1).padStart(2, '0')
    const day = String(d.getDate()).padStart(2, '0')
    return `${y}-${m}-${day}`
  },
  set: (s: string) => {
    form.expire = s ? Math.floor(new Date(s).getTime() / 1000) : null
  }
})

function randomUsername() {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
  let result = ''
  for (let i = 0; i < 8; i++) result += chars.charAt(Math.floor(Math.random() * chars.length))
  form.username = result
}

function toggleProtocol(protocol: ProxyKey, checked: boolean) {
  if (checked) {
    if (!form.selected_proxies.includes(protocol)) form.selected_proxies.push(protocol)
  } else {
    form.selected_proxies = form.selected_proxies.filter((p) => p !== protocol)
  }
}

function isInboundChecked(protocol: string, tag: string) {
  return (form.inbounds[protocol] ?? []).includes(tag)
}

function toggleInbound(protocol: string, tag: string, checked: boolean) {
  const current = form.inbounds[protocol] ?? []
  if (checked) {
    if (!current.includes(tag)) form.inbounds[protocol] = [...current, tag]
  } else {
    form.inbounds[protocol] = current.filter((t) => t !== tag)
  }
}

function setNullableNumber(
  field: 'data_limit' | 'on_hold_expire_duration',
  value: string | number
) {
  if (value === '' || value === null || value === undefined) {
    form[field] = null
    return
  }
  const n = typeof value === 'number' ? value : Number(value)
  form[field] = Number.isFinite(n) ? n : null
}

function buildProxies(): UserCreate['proxies'] {
  const result: UserCreate['proxies'] = {}
  for (const key of form.selected_proxies) {
    if (key === 'vmess') result.vmess = form.proxies.vmess.id ? { id: form.proxies.vmess.id } : {}
    if (key === 'vless')
      result.vless = {
        ...(form.proxies.vless.id ? { id: form.proxies.vless.id } : {}),
        ...(form.proxies.vless.flow ? { flow: form.proxies.vless.flow } : {})
      }
    if (key === 'trojan')
      result.trojan = form.proxies.trojan.password ? { password: form.proxies.trojan.password } : {}
    if (key === 'shadowsocks')
      result.shadowsocks = {
        ...(form.proxies.shadowsocks.password
          ? { password: form.proxies.shadowsocks.password }
          : {}),
        ...(form.proxies.shadowsocks.method ? { method: form.proxies.shadowsocks.method } : {})
      }
  }
  return result
}

function buildInbounds(): Record<string, string[]> {
  const inbounds: Record<string, string[]> = {}
  for (const protocol of form.selected_proxies) {
    const tags = form.inbounds[protocol]
    if (Array.isArray(tags) && tags.length) inbounds[protocol] = tags
  }
  return inbounds
}

const submitting = ref(false)

async function onSubmit() {
  if (!validate()) return

  errorMsg.value = ''
  const dataLimitBytes = form.data_limit ? Number((form.data_limit * GB).toFixed(0)) : 0

  const body: UserCreate = {
    username: form.username,
    proxies: buildProxies(),
    inbounds: buildInbounds(),
    data_limit: dataLimitBytes,
    data_limit_reset_strategy:
      dataLimitBytes > 0 ? (form.data_limit_reset_strategy as any) : 'no_reset',
    status: form.status,
    expire: form.status === 'on_hold' ? null : form.expire,
    on_hold_expire_duration:
      form.status === 'on_hold' && form.on_hold_expire_duration
        ? Math.round(form.on_hold_expire_duration * DAY)
        : null,
    note: form.note
  }

  submitting.value = true
  try {
    if (isEditing.value) await updateUser.mutateAsync(body)
    else await createUser.mutateAsync(body)
    emit('update:modelValue', false)
    toast.success(
      t(isEditing.value ? 'userDialog.userEdited' : 'userDialog.userCreated', {
        username: form.username
      })
    )
  } catch (err: unknown) {
    const detail = extractErrorDetail(err)
    errorMsg.value =
      typeof detail === 'string' ? detail : detail ? Object.values(detail).join(', ') : String(err)
  } finally {
    submitting.value = false
  }
}

function close() {
  emit('update:modelValue', false)
}
</script>

<template>
  <Dialog
    :open="modelValue"
    @update:open="(v: boolean) => emit('update:modelValue', v)"
  >
    <DialogContent class="max-h-[90vh] overflow-y-auto sm:max-w-2xl">
      <DialogHeader>
        <DialogTitle>
          {{ isEditing ? t('userDialog.editUserTitle') : t('createNewUser') }}
        </DialogTitle>
      </DialogHeader>

      <form class="grid gap-4" @submit.prevent="onSubmit">
        <div class="space-y-2">
          <Label for="user-username">{{ t('username') }}</Label>
          <div class="flex gap-2">
            <Input
              id="user-username"
              v-model="form.username"
              class="flex-1"
              :disabled="isEditing"
              :aria-invalid="!!fieldErrors.username"
            />
            <Button
              v-if="!isEditing"
              type="button"
              variant="outline"
              size="icon"
              @click="randomUsername"
            >
              <RefreshCw class="size-4" />
            </Button>
          </div>
          <p v-if="fieldErrors.username" class="text-xs text-destructive">
            {{ fieldErrors.username }}
          </p>
        </div>

        <div class="space-y-2">
          <Label>{{ t('userDialog.protocols') }}</Label>
          <div class="flex flex-wrap gap-3">
            <label
              v-for="p in ALL_PROTOCOLS"
              :key="p"
              class="flex items-center gap-2 text-sm text-foreground"
            >
              <input
                type="checkbox"
                class="size-4 rounded border border-input accent-primary"
                :checked="form.selected_proxies.includes(p)"
                @change="
                  toggleProtocol(p, ($event.target as HTMLInputElement).checked)
                "
              />
              <span>{{ p }}</span>
            </label>
          </div>
          <p v-if="fieldErrors.selected_proxies" class="text-xs text-destructive">
            {{ fieldErrors.selected_proxies }}
          </p>
        </div>

        <div v-if="form.selected_proxies.includes('vless')" class="space-y-2">
          <Label>VLESS flow</Label>
          <Select
            :model-value="toFlowSelect(form.proxies.vless.flow)"
            @update:model-value="(v) => (form.proxies.vless.flow = fromFlowSelect(v))"
          >
            <SelectTrigger class="w-full">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem
                v-for="f in VLESS_FLOWS"
                :key="toFlowSelect(f)"
                :value="toFlowSelect(f)"
              >
                {{ f || 'none' }}
              </SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div v-if="form.selected_proxies.includes('shadowsocks')" class="space-y-2">
          <Label>{{ t('userDialog.method') }}</Label>
          <Select
            :model-value="form.proxies.shadowsocks.method"
            @update:model-value="(v) => (form.proxies.shadowsocks.method = String(v))"
          >
            <SelectTrigger class="w-full">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem v-for="m in SS_METHODS" :key="m" :value="m">
                {{ m }}
              </SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div
          v-for="protocol in form.selected_proxies"
          :key="protocol"
          class="space-y-2"
        >
          <Label>{{ `${t('inbound')} · ${protocol}` }}</Label>
          <div v-if="tagsFor(protocol).length" class="flex flex-wrap gap-3">
            <label
              v-for="tag in tagsFor(protocol)"
              :key="tag"
              class="flex items-center gap-2 text-sm text-foreground"
            >
              <input
                type="checkbox"
                class="size-4 rounded border border-input accent-primary"
                :checked="isInboundChecked(protocol, tag)"
                @change="
                  toggleInbound(protocol, tag, ($event.target as HTMLInputElement).checked)
                "
              />
              <span>{{ tag }}</span>
            </label>
          </div>
          <p v-else class="text-xs text-muted-foreground">{{ protocol }}</p>
        </div>

        <div class="grid gap-4 sm:grid-cols-2">
          <div class="space-y-2">
            <Label for="user-data-limit">{{ t('userDialog.dataLimit') + ' (GB)' }}</Label>
            <Input
              id="user-data-limit"
              type="number"
              min="0"
              step="1"
              :model-value="form.data_limit ?? ''"
              :placeholder="t('userDialog.generatedByDefault')"
              @update:model-value="(v) => setNullableNumber('data_limit', v)"
            />
          </div>
          <div
            v-if="form.data_limit && form.data_limit > 0"
            class="space-y-2"
          >
            <Label>{{ t('userDialog.periodicUsageReset') }}</Label>
            <Select
              :model-value="form.data_limit_reset_strategy"
              @update:model-value="(v) => (form.data_limit_reset_strategy = String(v))"
            >
              <SelectTrigger class="w-full">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem
                  v-for="s in RESET_STRATEGIES"
                  :key="s.value"
                  :value="s.value"
                >
                  {{ t(`userDialog.${s.title}`) }}
                </SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <div class="space-y-2">
          <Label>{{ t('status.active') + ' / ' + t('userDialog.onHold') }}</Label>
          <Select
            :model-value="form.status"
            @update:model-value="(v) => (form.status = String(v) as 'active' | 'on_hold')"
          >
            <SelectTrigger class="w-full">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="active">{{ t('status.active') }}</SelectItem>
              <SelectItem value="on_hold">{{ t('userDialog.onHold') }}</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div v-if="form.status === 'on_hold'" class="space-y-2">
          <Label for="user-on-hold">
            {{ t('userDialog.onHoldExpireDuration') + ' (' + t('userDialog.days') + ')' }}
          </Label>
          <Input
            id="user-on-hold"
            type="number"
            min="0"
            step="1"
            :model-value="form.on_hold_expire_duration ?? ''"
            @update:model-value="(v) => setNullableNumber('on_hold_expire_duration', v)"
          />
        </div>
        <div v-else class="space-y-2">
          <Label for="user-expire">{{ t('userDialog.expiryDate') }}</Label>
          <Input
            id="user-expire"
            type="date"
            :model-value="expireDateStr"
            :placeholder="t('userDialog.optional')"
            @update:model-value="(v) => (expireDateStr = String(v))"
          />
        </div>

        <div class="space-y-2">
          <Label for="user-note">{{ t('userDialog.note') }}</Label>
          <textarea
            id="user-note"
            v-model="form.note"
            rows="2"
            class="w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm text-foreground shadow-xs outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
          />
        </div>

        <Alert v-if="errorMsg" variant="destructive">
          <AlertDescription>{{ errorMsg }}</AlertDescription>
        </Alert>
      </form>

      <DialogFooter class="sm:justify-between">
        <div v-if="isEditing && user" class="flex flex-wrap gap-1">
          <Button variant="ghost" type="button" @click="emit('resetUsage', user)">
            {{ t('userDialog.resetUsage') }}
          </Button>
          <Button variant="ghost" type="button" @click="emit('revokeSub', user)">
            {{ t('userDialog.revokeSubscription') }}
          </Button>
        </div>
        <div v-else />
        <div class="flex gap-2">
          <Button variant="outline" type="button" @click="close">
            {{ t('cancel') }}
          </Button>
          <Button type="button" :disabled="submitting" @click="onSubmit">
            <Loader2 v-if="submitting" class="size-4 animate-spin" />
            {{ isEditing ? t('core.save') : t('createUser') }}
          </Button>
        </div>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
