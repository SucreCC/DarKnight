<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { extractErrorDetail } from '@/config/axios'
import { useInboundsQuery, useUserMutations } from '@/api/user'
import {
  RESET_STRATEGIES,
  type Inbounds,
  type ProxyKey,
  type User,
  type UserCreate
} from '@/api/user/types'

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
const VLESS_FLOWS = ['', 'xtls-rprx-vision']

const isEditing = computed(() => !!props.user)
const errorMsg = ref('')
const formRef = ref<FormInstance>()

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

const rules: FormRules = {
  username: [{ required: true, message: () => t('login.fieldRequired'), trigger: 'blur' }],
  selected_proxies: [
    {
      validator: (_r, value: ProxyKey[], cb) =>
        value && value.length > 0 ? cb() : cb(new Error(t('userDialog.selectOneProtocol'))),
      trigger: 'change'
    }
  ]
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
    if (!open) return
    if (props.user) loadUser(props.user)
    else resetToDefault()
  }
)

const expireDate = computed<Date | null>({
  get: () => (form.expire ? new Date(form.expire * 1000) : null),
  set: (d) => {
    form.expire = d ? Math.floor(d.getTime() / 1000) : null
  }
})

function randomUsername() {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
  let result = ''
  for (let i = 0; i < 8; i++) result += chars.charAt(Math.floor(Math.random() * chars.length))
  form.username = result
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
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

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
    ElMessage.success(
      t(isEditing.value ? 'userDialog.userEdited' : 'userDialog.userCreated', {
        username: form.username
      })
    )
    emit('update:modelValue', false)
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
  <el-dialog
    :model-value="modelValue"
    :title="isEditing ? t('userDialog.editUserTitle') : t('createNewUser')"
    width="640px"
    @update:model-value="(v: boolean) => emit('update:modelValue', v)"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
      <el-form-item :label="t('username')" prop="username">
        <div class="username-row">
          <el-input v-model="form.username" :disabled="isEditing" />
          <el-button v-if="!isEditing" :icon="Refresh" @click="randomUsername" />
        </div>
      </el-form-item>

      <el-form-item :label="t('userDialog.protocols')" prop="selected_proxies">
        <el-checkbox-group v-model="form.selected_proxies">
          <el-checkbox v-for="p in ALL_PROTOCOLS" :key="p" :value="p" :label="p" />
        </el-checkbox-group>
      </el-form-item>

      <el-form-item v-if="form.selected_proxies.includes('vless')" label="VLESS flow">
        <el-select v-model="form.proxies.vless.flow" style="width: 100%">
          <el-option v-for="f in VLESS_FLOWS" :key="f" :label="f || 'none'" :value="f" />
        </el-select>
      </el-form-item>

      <el-form-item
        v-if="form.selected_proxies.includes('shadowsocks')"
        :label="t('userDialog.method')"
      >
        <el-select v-model="form.proxies.shadowsocks.method" style="width: 100%">
          <el-option v-for="m in SS_METHODS" :key="m" :label="m" :value="m" />
        </el-select>
      </el-form-item>

      <el-form-item
        v-for="protocol in form.selected_proxies"
        :key="protocol"
        :label="`${t('inbound')} · ${protocol}`"
      >
        <el-select
          v-model="form.inbounds[protocol]"
          multiple
          collapse-tags
          collapse-tags-tooltip
          style="width: 100%"
          :placeholder="protocol"
        >
          <el-option v-for="tag in tagsFor(protocol)" :key="tag" :label="tag" :value="tag" />
        </el-select>
      </el-form-item>

      <div class="grid-2">
        <el-form-item :label="t('userDialog.dataLimit') + ' (GB)'">
          <el-input-number
            v-model="form.data_limit"
            :min="0"
            :step="1"
            :controls="false"
            style="width: 100%"
            :placeholder="t('userDialog.generatedByDefault')"
          />
        </el-form-item>
        <el-form-item
          v-if="form.data_limit && form.data_limit > 0"
          :label="t('userDialog.periodicUsageReset')"
        >
          <el-select v-model="form.data_limit_reset_strategy" style="width: 100%">
            <el-option
              v-for="s in RESET_STRATEGIES"
              :key="s.value"
              :label="t(`userDialog.${s.title}`)"
              :value="s.value"
            />
          </el-select>
        </el-form-item>
      </div>

      <el-form-item :label="t('status.active') + ' / ' + t('userDialog.onHold')">
        <el-radio-group v-model="form.status">
          <el-radio-button value="active">{{ t('status.active') }}</el-radio-button>
          <el-radio-button value="on_hold">{{ t('userDialog.onHold') }}</el-radio-button>
        </el-radio-group>
      </el-form-item>

      <el-form-item
        v-if="form.status === 'on_hold'"
        :label="t('userDialog.onHoldExpireDuration') + ' (' + t('userDialog.days') + ')'"
      >
        <el-input-number
          v-model="form.on_hold_expire_duration"
          :min="0"
          :step="1"
          :controls="false"
          style="width: 100%"
        />
      </el-form-item>
      <el-form-item v-else :label="t('userDialog.expiryDate')">
        <el-date-picker
          v-model="expireDate"
          type="date"
          style="width: 100%"
          :placeholder="t('userDialog.optional')"
        />
      </el-form-item>

      <el-form-item :label="t('userDialog.note')">
        <el-input v-model="form.note" type="textarea" :rows="2" />
      </el-form-item>

      <el-alert v-if="errorMsg" :title="errorMsg" type="error" :closable="false" show-icon />
    </el-form>

    <template #footer>
      <div class="footer">
        <div v-if="isEditing && user" class="footer-left">
          <el-button text @click="emit('resetUsage', user)">
            {{ t('userDialog.resetUsage') }}
          </el-button>
          <el-button text @click="emit('revokeSub', user)">
            {{ t('userDialog.revokeSubscription') }}
          </el-button>
        </div>
        <div class="dk-spacer" />
        <el-button @click="close">{{ t('cancel') }}</el-button>
        <el-button type="primary" :loading="submitting" @click="onSubmit">
          {{ isEditing ? t('core.save') : t('createUser') }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<style scoped>
.username-row {
  display: flex;
  gap: 8px;
  width: 100%;
}

.grid-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.footer {
  display: flex;
  align-items: center;
  gap: 8px;
}

.footer-left {
  display: flex;
  gap: 4px;
}
</style>
