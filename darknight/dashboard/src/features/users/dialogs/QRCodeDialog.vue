<script setup lang="ts">
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import QrcodeVue from "qrcode.vue";
import { ElMessage } from "element-plus";
import type { User } from "../types";
import { absoluteSubscriptionUrl } from "../helpers";

const props = defineProps<{
  modelValue: boolean;
  user: User | null;
}>();
const emit = defineEmits<{ "update:modelValue": [value: boolean] }>();

const { t } = useI18n();

const subUrl = computed(() =>
  props.user ? absoluteSubscriptionUrl(props.user.subscription_url) : ""
);
const links = computed(() => props.user?.links ?? []);

async function copySub() {
  await navigator.clipboard.writeText(subUrl.value);
  ElMessage.success(t("usersTable.copied"));
}
</script>

<template>
  <el-dialog
    :model-value="modelValue"
    :title="t('qrcodeDialog.sublink')"
    width="420px"
    @update:model-value="(v: boolean) => emit('update:modelValue', v)"
  >
    <div class="qr-wrap">
      <QrcodeVue v-if="subUrl" :value="subUrl" :size="220" level="M" />
      <el-input
        :model-value="subUrl"
        readonly
        class="sub-input"
        @click="copySub"
      />
      <el-divider v-if="links.length">Configs</el-divider>
      <div v-if="links.length" class="links-grid">
        <div v-for="(link, i) in links" :key="i" class="link-qr">
          <QrcodeVue :value="link" :size="120" level="M" />
        </div>
      </div>
    </div>
  </el-dialog>
</template>

<style scoped>
.qr-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}
.sub-input {
  width: 100%;
  cursor: pointer;
}
.links-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  justify-content: center;
}
</style>
