<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import {
  buildLogsWebsocketUrl,
  useCoreConfigQuery,
  useCoreQuery,
  useRestartCore,
  useUpdateConfig
} from '@/api/setting'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'

const { t } = useI18n()
const { data: core } = useCoreQuery()
const { data: config } = useCoreConfigQuery()
const updateConfig = useUpdateConfig()
const restartCore = useRestartCore()

const configText = ref('')

watch(
  config,
  (value) => {
    if (value) configText.value = JSON.stringify(value, null, 2)
  },
  { immediate: true }
)

async function onSave() {
  let parsed: Record<string, unknown>
  try {
    parsed = JSON.parse(configText.value)
  } catch {
    toast.error('Invalid JSON')
    return
  }
  try {
    await updateConfig.mutateAsync(parsed)
    toast.success(t('core.successMessage'))
  } catch {
    toast.error(t('core.generalErrorMessage'))
  }
}

async function onRestart() {
  try {
    await restartCore.mutateAsync()
    toast.success(t('core.restarting'))
  } catch {
    toast.error(t('core.generalErrorMessage'))
  }
}

const logs = ref<string[]>([])
const logsBox = ref<HTMLElement>()
let socket: WebSocket | null = null

function connectLogs() {
  const url = buildLogsWebsocketUrl()
  if (!url) return
  socket = new WebSocket(url)
  socket.onmessage = async (event) => {
    logs.value.push(String(event.data))
    if (logs.value.length > 500) logs.value.splice(0, logs.value.length - 500)
    await nextTick()
    if (logsBox.value) logsBox.value.scrollTop = logsBox.value.scrollHeight
  }
}

onMounted(connectLogs)
onBeforeUnmount(() => {
  socket?.close()
  socket = null
})
</script>

<template>
  <div class="flex max-w-6xl flex-col gap-4">
    <div class="flex flex-wrap items-center gap-3">
      <span class="inline-flex items-center gap-2 font-semibold text-foreground">
        Xray {{ core?.version || '-' }}
        <Badge :variant="core?.started ? 'default' : 'secondary'">
          {{ core?.started ? t('core.socket.connected') : t('core.socket.not_connected') }}
        </Badge>
      </span>
      <div class="flex-1" />
      <Button variant="outline" :disabled="restartCore.isPending.value" @click="onRestart">
        {{ t('core.restartCore') }}
      </Button>
      <Button :disabled="updateConfig.isPending.value" @click="onSave">
        {{ t('core.save') }}
      </Button>
    </div>

    <div class="grid gap-4 lg:grid-cols-[1.4fr_1fr]">
      <div class="rounded-xl border border-border bg-card p-4">
        <div class="mb-2 font-semibold text-foreground">{{ t('core.configuration') }}</div>
        <textarea
          v-model="configText"
          rows="24"
          spellcheck="false"
          class="w-full rounded-lg border border-input bg-background p-3 font-mono text-xs text-foreground outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
        />
      </div>
      <div class="rounded-xl border border-border bg-card p-4">
        <div class="mb-2 font-semibold text-foreground">{{ t('core.logs') }}</div>
        <div
          ref="logsBox"
          class="h-[520px] overflow-y-auto rounded-lg bg-muted p-2.5 font-mono text-xs break-all whitespace-pre-wrap text-foreground"
        >
          <div v-for="(line, i) in logs" :key="i" class="leading-normal">{{ line }}</div>
        </div>
      </div>
    </div>
  </div>
</template>
