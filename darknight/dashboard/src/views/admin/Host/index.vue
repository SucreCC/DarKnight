<script setup lang="ts">
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import { Loader2, Plus, Save } from 'lucide-vue-next'
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

const inboundTags = ref<string[]>([])

watch(
  model,
  (value) => {
    inboundTags.value = Object.keys(value)
  },
  { immediate: true, deep: true }
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
  <div class="relative flex max-w-6xl flex-col gap-5">
    <div
      v-if="isFetching"
      class="absolute inset-0 z-10 flex items-center justify-center rounded-xl bg-background/60"
    >
      <Loader2 class="size-8 animate-spin text-primary" />
    </div>

    <div class="flex flex-wrap items-start justify-between gap-3">
      <div>
        <h1 class="text-lg font-semibold text-foreground">{{ t('hosts.pageTitle') }}</h1>
        <p class="mt-1 max-w-2xl text-sm text-muted-foreground">{{ t('hosts.pageDesc') }}</p>
      </div>
      <Button :disabled="saveHosts.isPending.value" @click="onSave">
        <Loader2 v-if="saveHosts.isPending.value" class="mr-2 size-4 animate-spin" />
        <Save v-else class="mr-2 size-4" />
        {{ t('hostsDialog.apply') }}
      </Button>
    </div>

    <div
      v-if="!isFetching && !inboundTags.length"
      class="rounded-xl border border-border bg-card px-4 py-10 text-center text-sm text-muted-foreground"
    >
      {{ t('hosts.noInbounds') }}
    </div>

    <details
      v-for="tag in inboundTags"
      :key="tag"
      class="rounded-xl border border-border bg-card p-4 shadow-sm"
      open
    >
      <summary class="cursor-pointer list-none font-semibold text-foreground">
        <span class="inline-flex items-center gap-2">
          <span class="rounded-md bg-primary/10 px-2 py-0.5 text-xs font-medium text-primary">
            {{ t('hostsDialog.title') }}
          </span>
          {{ tag }}
        </span>
      </summary>
      <div class="mt-4 space-y-3">
        <p
          v-if="!(model[tag] ?? []).length"
          class="rounded-lg border border-dashed border-border px-4 py-6 text-center text-sm text-muted-foreground"
        >
          {{ t('hosts.empty') }}
        </p>
        <HostForm
          v-for="(host, index) in model[tag]"
          :key="index"
          :model-value="host"
          @update:model-value="(v) => updateHost(tag, index, v)"
          @remove="removeHost(tag, index)"
        />
        <Button variant="outline" type="button" @click="addHost(tag)">
          <Plus class="mr-2 size-4" />
          {{ t('hostsDialog.addHost') }}
        </Button>
      </div>
    </details>
  </div>
</template>
