<script setup lang="ts">
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import { Loader2, Plus } from 'lucide-vue-next'
import { extractErrorDetail } from '@/config/axios'
import { useHostsQuery, useSaveHosts } from '@/api/host'
import { defaultHost, type HostEntry, type HostsSchema } from '@/api/host/types'
import { Button } from '@/components/ui/button'
import HostForm from './components/HostForm.vue'

const { t } = useI18n()
const { data, isFetching } = useHostsQuery()
const saveHosts = useSaveHosts()

const model = ref<HostsSchema>({})

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
    toast.success(t('hostsDialog.savedSuccess'))
  } catch (err: unknown) {
    const detail = extractErrorDetail(err)
    toast.error(typeof detail === 'string' ? detail : t('core.generalErrorMessage'))
  }
}
</script>

<template>
  <div class="relative flex max-w-6xl flex-col gap-4">
    <div
      v-if="isFetching"
      class="absolute inset-0 z-10 flex items-center justify-center rounded-xl bg-background/60"
    >
      <Loader2 class="size-8 animate-spin text-primary" />
    </div>

    <div class="flex flex-wrap items-center gap-3">
      <span class="text-sm text-muted-foreground">{{ t('hostsDialog.title') }}</span>
      <div class="flex-1" />
      <Button :disabled="saveHosts.isPending.value" @click="onSave">
        <Loader2 v-if="saveHosts.isPending.value" class="size-4 animate-spin" />
        {{ t('hostsDialog.apply') }}
      </Button>
    </div>

    <details
      v-for="(entries, tag) in model"
      :key="tag"
      class="mb-4 rounded-xl border border-border bg-card p-4"
      open
    >
      <summary class="cursor-pointer font-semibold text-foreground">{{ tag }}</summary>
      <div class="mt-4 space-y-3">
        <HostForm
          v-for="(host, index) in entries"
          :key="index"
          :model-value="host"
          @update:model-value="(v) => updateHost(String(tag), index, v)"
          @remove="removeHost(String(tag), index)"
        />
        <Button variant="outline" type="button" @click="addHost(String(tag))">
          <Plus class="size-4" />
          {{ t('hostsDialog.addHost') }}
        </Button>
      </div>
    </details>
  </div>
</template>
