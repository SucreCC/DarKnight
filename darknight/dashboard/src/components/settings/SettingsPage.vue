<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch, nextTick } from "vue";
import { useI18n } from "vue-i18n";
import { ElMessage } from "element-plus";
import {
  buildLogsWebsocketUrl,
  useCoreConfigQuery,
  useCoreQuery,
  useRestartCore,
  useUpdateConfig,
} from "./api";

const { t } = useI18n();
const { data: core } = useCoreQuery();
const { data: config } = useCoreConfigQuery();
const updateConfig = useUpdateConfig();
const restartCore = useRestartCore();

const configText = ref("");

watch(
  config,
  (value) => {
    if (value) configText.value = JSON.stringify(value, null, 2);
  },
  { immediate: true }
);

async function onSave() {
  let parsed: Record<string, unknown>;
  try {
    parsed = JSON.parse(configText.value);
  } catch {
    ElMessage.error("Invalid JSON");
    return;
  }
  try {
    await updateConfig.mutateAsync(parsed);
    ElMessage.success(t("core.successMessage"));
  } catch {
    ElMessage.error(t("core.generalErrorMessage"));
  }
}

async function onRestart() {
  try {
    await restartCore.mutateAsync();
    ElMessage.success(t("core.restarting"));
  } catch {
    ElMessage.error(t("core.generalErrorMessage"));
  }
}

// ---- logs websocket ----
const logs = ref<string[]>([]);
const logsBox = ref<HTMLElement>();
let socket: WebSocket | null = null;

function connectLogs() {
  const url = buildLogsWebsocketUrl();
  if (!url) return;
  socket = new WebSocket(url);
  socket.onmessage = async (event) => {
    logs.value.push(String(event.data));
    if (logs.value.length > 500) logs.value.splice(0, logs.value.length - 500);
    await nextTick();
    if (logsBox.value) logsBox.value.scrollTop = logsBox.value.scrollHeight;
  };
}

onMounted(connectLogs);
onBeforeUnmount(() => {
  socket?.close();
  socket = null;
});
</script>

<template>
  <div class="dk-page">
    <div class="dk-toolbar">
      <span class="version">
        Xray {{ core?.version || "-" }}
        <el-tag
          :type="core?.started ? 'success' : 'info'"
          size="small"
          round
        >
          {{ core?.started ? t("core.socket.connected") : t("core.socket.not_connected") }}
        </el-tag>
      </span>
      <div class="dk-spacer" />
      <el-button :loading="restartCore.isPending.value" @click="onRestart">
        {{ t("core.restartCore") }}
      </el-button>
      <el-button
        type="primary"
        :loading="updateConfig.isPending.value"
        @click="onSave"
      >
        {{ t("core.save") }}
      </el-button>
    </div>

    <el-row :gutter="16">
      <el-col :span="14">
        <div class="section-title">{{ t("core.configuration") }}</div>
        <el-input
          v-model="configText"
          type="textarea"
          :rows="24"
          class="config-editor"
          spellcheck="false"
        />
      </el-col>
      <el-col :span="10">
        <div class="section-title">{{ t("core.logs") }}</div>
        <div ref="logsBox" class="logs-box">
          <div v-for="(line, i) in logs" :key="i" class="log-line">{{ line }}</div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.version {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}
.section-title {
  font-weight: 600;
  margin-bottom: 8px;
}
.config-editor :deep(textarea) {
  font-family: "JetBrains Mono", Consolas, monospace;
  font-size: 12px;
}
.logs-box {
  height: 520px;
  overflow-y: auto;
  background: var(--el-fill-color-darker);
  border-radius: 6px;
  padding: 10px;
  font-family: Consolas, monospace;
  font-size: 12px;
  white-space: pre-wrap;
  word-break: break-all;
}
.log-line {
  line-height: 1.5;
}
</style>
