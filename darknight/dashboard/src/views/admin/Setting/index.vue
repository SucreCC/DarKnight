<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  Activity,
  Circle,
  FileJson,
  Loader2,
  RotateCcw,
  Save,
  ScrollText
} from 'lucide-vue-next'
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
import { Skeleton } from '@/components/ui/skeleton'

const { t } = useI18n()
const { data: core, isLoading: coreLoading } = useCoreQuery()
const { data: config, isLoading: configLoading } = useCoreConfigQuery()
const updateConfig = useUpdateConfig()
const restartCore = useRestartCore()

const configText = ref('')
const logsConnected = ref(false)

watch(
  config,
  (value) => {
    if (value) configText.value = JSON.stringify(value, null, 2)
  },
  { immediate: true }
)

const isRunning = computed(() => core.value?.started === true)
const configLines = computed(() =>
  configText.value ? configText.value.split('\n').length : 0
)

async function onSave() {
  let parsed: Record<string, unknown>
  try {
    parsed = JSON.parse(configText.value)
  } catch {
    toast.error(t('core.invalidJson'))
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
  socket.onopen = () => {
    logsConnected.value = true
  }
  socket.onclose = () => {
    logsConnected.value = false
  }
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
  <div class="flex max-w-6xl flex-col gap-5">
    <div class="flex flex-wrap items-start justify-between gap-4">
      <div>
        <h1 class="text-lg font-semibold text-foreground">{{ t('core.pageTitle') }}</h1>
        <p class="mt-1 max-w-2xl text-sm text-muted-foreground">{{ t('core.pageDesc') }}</p>
      </div>
      <div class="flex flex-wrap items-center gap-2">
        <Button
          variant="outline"
          :disabled="restartCore.isPending.value"
          @click="onRestart"
        >
          <Loader2 v-if="restartCore.isPending.value" class="mr-2 size-4 animate-spin" />
          <RotateCcw v-else class="mr-2 size-4" />
          {{ t('core.restartCore') }}
        </Button>
        <Button :disabled="updateConfig.isPending.value || configLoading" @click="onSave">
          <Loader2 v-if="updateConfig.isPending.value" class="mr-2 size-4 animate-spin" />
          <Save v-else class="mr-2 size-4" />
          {{ t('core.save') }}
        </Button>
      </div>
    </div>

    <div class="grid gap-3 sm:grid-cols-3">
      <div class="rounded-2xl border border-slate-200/80 bg-card p-4 shadow-sm dark:border-border">
        <div class="flex items-center gap-3">
          <div
            class="flex size-10 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary"
          >
            <Activity class="size-5" />
          </div>
          <div class="min-w-0">
            <p class="text-xs text-muted-foreground">{{ t('core.runtimeStatus') }}</p>
            <Skeleton v-if="coreLoading" class="mt-2 h-6 w-20" />
            <Badge v-else class="mt-1" :variant="isRunning ? 'default' : 'secondary'">
              {{ isRunning ? t('core.socket.connected') : t('core.socket.not_connected') }}
            </Badge>
          </div>
        </div>
      </div>

      <div class="rounded-2xl border border-slate-200/80 bg-card p-4 shadow-sm dark:border-border">
        <div class="flex items-center gap-3">
          <div
            class="flex size-10 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary"
          >
            <FileJson class="size-5" />
          </div>
          <div class="min-w-0">
            <p class="text-xs text-muted-foreground">{{ t('core.version') }}</p>
            <Skeleton v-if="coreLoading" class="mt-2 h-7 w-24" />
            <p v-else class="mt-0.5 truncate text-xl font-semibold tracking-tight text-foreground">
              {{ core?.version || '—' }}
            </p>
          </div>
        </div>
      </div>

      <div class="rounded-2xl border border-slate-200/80 bg-card p-4 shadow-sm dark:border-border">
        <div class="flex items-center gap-3">
          <div
            class="flex size-10 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary"
          >
            <ScrollText class="size-5" />
          </div>
          <div class="min-w-0">
            <p class="text-xs text-muted-foreground">{{ t('core.logStream') }}</p>
            <div class="mt-1 flex items-center gap-1.5">
              <Circle
                class="size-2 fill-current"
                :class="logsConnected ? 'text-emerald-500' : 'text-muted-foreground/50'"
              />
              <span class="text-sm font-medium text-foreground">
                {{
                  logsConnected ? t('core.socket.connected') : t('core.socket.not_connected')
                }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="grid gap-4 lg:grid-cols-[1.45fr_1fr]">
      <div
        class="flex min-h-[560px] flex-col overflow-hidden rounded-2xl border border-slate-200/80 bg-card shadow-sm dark:border-border"
      >
        <div class="flex items-start justify-between gap-3 border-b border-border px-4 py-3">
          <div class="min-w-0">
            <div class="flex items-center gap-2 font-semibold text-foreground">
              <FileJson class="size-4 text-primary" />
              {{ t('core.configuration') }}
            </div>
            <p class="mt-1 text-xs leading-relaxed text-muted-foreground">
              {{ t('core.configHint') }}
            </p>
          </div>
          <span
            v-if="!configLoading"
            class="shrink-0 rounded-md bg-muted px-2 py-1 text-xs text-muted-foreground"
          >
            {{ t('core.lineCount', { count: configLines }) }}
          </span>
        </div>

        <div class="min-h-0 flex-1 p-4">
          <div v-if="configLoading" class="space-y-2">
            <Skeleton v-for="i in 14" :key="i" class="h-4 w-full" />
          </div>
          <textarea
            v-else
            v-model="configText"
            spellcheck="false"
            class="h-[480px] w-full resize-none rounded-xl border border-input bg-muted/20 p-4 font-mono text-xs leading-relaxed text-foreground outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
          />
        </div>
      </div>

      <div
        class="flex min-h-[560px] flex-col overflow-hidden rounded-2xl border border-slate-200/80 bg-card shadow-sm dark:border-border"
      >
        <div class="flex items-center justify-between gap-3 border-b border-border px-4 py-3">
          <div class="flex items-center gap-2 font-semibold text-foreground">
            <ScrollText class="size-4 text-primary" />
            {{ t('core.logs') }}
          </div>
          <div class="flex items-center gap-1.5 text-xs text-muted-foreground">
            <Circle
              class="size-2 fill-current"
              :class="logsConnected ? 'text-emerald-500' : 'text-muted-foreground/50'"
            />
            {{ logsConnected ? t('core.logStreamLive') : t('core.logStreamIdle') }}
          </div>
        </div>

        <div
          ref="logsBox"
          class="min-h-0 flex-1 overflow-y-auto bg-zinc-950 p-4 font-mono text-xs leading-relaxed break-all whitespace-pre-wrap text-zinc-300"
        >
          <p v-if="!logs.length" class="text-zinc-500">{{ t('core.logsEmpty') }}</p>
          <div v-for="(line, i) in logs" :key="i">{{ line }}</div>
        </div>
      </div>
    </div>
  </div>
</template>
