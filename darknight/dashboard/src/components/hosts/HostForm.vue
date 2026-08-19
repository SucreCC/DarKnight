<script setup lang="ts">
import { useI18n } from "vue-i18n";
import { Delete } from "@element-plus/icons-vue";
import {
  ALPN_OPTIONS,
  FINGERPRINT_OPTIONS,
  HOST_SECURITY_OPTIONS,
  type HostEntry,
} from "./types";

const host = defineModel<HostEntry>({ required: true });
defineEmits<{ remove: [] }>();
const { t } = useI18n();
</script>

<template>
  <el-card class="host-card" shadow="never">
    <template #header>
      <div class="host-header">
        <el-input
          v-model="host.remark"
          placeholder="Remark"
          size="small"
          style="max-width: 220px"
        />
        <div class="dk-spacer" />
        <el-switch
          v-model="host.is_disabled"
          :active-text="t('status.disabled')"
          inline-prompt
        />
        <el-button
          size="small"
          text
          type="danger"
          :icon="Delete"
          @click="$emit('remove')"
        />
      </div>
    </template>

    <el-form label-position="top">
      <div class="grid-2">
        <el-form-item :label="t('hostsDialog.currentServer')">
          <el-input v-model="host.address" />
        </el-form-item>
        <el-form-item :label="t('hostsDialog.port')">
          <el-input-number
            v-model="host.port"
            :min="0"
            :controls="false"
            style="width: 100%"
          />
        </el-form-item>
      </div>

      <div class="grid-2">
        <el-form-item :label="t('hostsDialog.host')">
          <el-input v-model="host.host" />
        </el-form-item>
        <el-form-item :label="t('hostsDialog.sni')">
          <el-input v-model="host.sni" />
        </el-form-item>
      </div>

      <el-form-item :label="t('hostsDialog.path')">
        <el-input v-model="host.path" />
      </el-form-item>

      <div class="grid-3">
        <el-form-item :label="t('hostsDialog.security')">
          <el-select v-model="host.security" style="width: 100%">
            <el-option
              v-for="s in HOST_SECURITY_OPTIONS"
              :key="s.value"
              :label="s.title"
              :value="s.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('hostsDialog.alpn')">
          <el-select v-model="host.alpn" style="width: 100%">
            <el-option
              v-for="a in ALPN_OPTIONS"
              :key="a"
              :label="a || 'default'"
              :value="a"
            />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('hostsDialog.fingerprint')">
          <el-select v-model="host.fingerprint" style="width: 100%">
            <el-option
              v-for="f in FINGERPRINT_OPTIONS"
              :key="f"
              :label="f || 'default'"
              :value="f"
            />
          </el-select>
        </el-form-item>
      </div>

      <el-collapse>
        <el-collapse-item :title="t('hostsDialog.advancedOptions')">
          <el-form-item :label="t('hostsDialog.fragment')">
            <el-input
              v-model="host.fragment_setting"
              :placeholder="t('hostsDialog.fragment.info')"
            />
          </el-form-item>
          <el-form-item :label="t('hostsDialog.noise')">
            <el-input
              v-model="host.noise_setting"
              :placeholder="t('hostsDialog.noise.info')"
            />
          </el-form-item>
          <div class="switches">
            <el-checkbox v-model="host.allowinsecure">
              {{ t("hostsDialog.allowinsecure") }}
            </el-checkbox>
            <el-checkbox v-model="host.mux_enable">
              {{ t("hostsDialog.muxEnable") }}
            </el-checkbox>
            <el-checkbox v-model="host.random_user_agent">
              {{ t("hostsDialog.randomUserAgent") }}
            </el-checkbox>
            <el-checkbox v-model="host.use_sni_as_host">
              {{ t("hostsDialog.useSniAsHost") }}
            </el-checkbox>
          </div>
        </el-collapse-item>
      </el-collapse>
    </el-form>
  </el-card>
</template>

<style scoped>
.host-card {
  margin-bottom: 12px;
}
.host-header {
  display: flex;
  align-items: center;
  gap: 10px;
}
.grid-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
.grid-3 {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}
.switches {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}
</style>
