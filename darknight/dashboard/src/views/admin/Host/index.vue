<script setup lang="ts">
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { extractErrorDetail } from '@/config/axios'
import { useHostsQuery, useSaveHosts } from '@/api/host'
import { defaultHost, type HostEntry, type HostsSchema } from '@/api/host/types'
import HostForm from './components/HostForm.vue'

const { t } = useI18n()
const { data, isFetching } = useHostsQuery()
const saveHosts = useSaveHosts()

const model = ref<HostsSchema>({})
const activeTags = ref<string[]>([])

function normalize(hosts: HostsSchema): HostsSchema {
  const result: HostsSchema = {}
  for (const [tag, entries] of Object.entries(hosts)) {
    result[tag] = (entries ?? []).map((e) => {
      const merged = { ...defaultHost(), ...e }
      merged.allowinsecure = !!merged.allowinsecure
      merged.is_disabled = !!merged.is_disabled
      merged.mux_enable = !!merged.mux_enable
      merged.random_user_agent = !!merged.random_user_agent
      merged.use_sni_as_host = !!merged.use_sni_as_host
      return merged
    })
  }
  return result
}

watch(
  data,
  (value) => {
    if (!value) return
    model.value = normalize(value)
    activeTags.value = Object.keys(model.value)
  },
  { immediate: true }
)

function addHost(tag: string) {
  model.value[tag] = [...(model.value[tag] ?? []), defaultHost()]
}

function removeHost(tag: string, index: number) {
  model.value[tag].splice(index, 1)
}

function updateHost(tag: string, index: number, value: HostEntry) {
  model.value[tag][index] = value
}

async function onSave() {
  try {
    await saveHosts.mutateAsync(model.value)
    ElMessage.success(t('hostsDialog.savedSuccess'))
  } catch (err: unknown) {
    const detail = extractErrorDetail(err)
    ElMessage.error(typeof detail === 'string' ? detail : t('core.generalErrorMessage'))
  }
}
</script>

<template>
  <div class="dk-page" v-loading="isFetching">
    <div class="dk-toolbar">
      <span class="hint">{{ t('hostsDialog.title') }}</span>
      <div class="dk-spacer" />
      <el-button type="primary" :loading="saveHosts.isPending.value" @click="onSave">
        {{ t('hostsDialog.apply') }}
      </el-button>
    </div>

    <el-collapse v-model="activeTags">
      <el-collapse-item v-for="(entries, tag) in model" :key="tag" :name="tag" :title="tag">
        <HostForm
          v-for="(host, index) in entries"
          :key="index"
          :model-value="host"
          @update:model-value="(v) => updateHost(tag, index, v)"
          @remove="removeHost(tag, index)"
        />
        <el-button :icon="Plus" @click="addHost(tag)">
          {{ t('hostsDialog.addHost') }}
        </el-button>
      </el-collapse-item>
    </el-collapse>
  </div>
</template>

<style scoped>
.hint {
  font-size: 13px;
  color: var(--el-text-color-secondary);
}
</style>
