<script setup lang="ts">
import { computed, reactive, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { ElMessage, type FormInstance, type FormRules } from "element-plus";
import { useNodeMutations } from "../api";
import { defaultNode, type NodeType } from "../types";

const props = defineProps<{ modelValue: boolean; node: NodeType | null }>();
const emit = defineEmits<{ "update:modelValue": [value: boolean] }>();

const { t } = useI18n();
const { addNode, updateNode } = useNodeMutations();

const isEditing = computed(() => !!props.node);
const formRef = ref<FormInstance>();
const errorMsg = ref("");
const form = reactive<NodeType>(defaultNode());

const rules: FormRules = {
  name: [{ required: true, message: () => t("login.fieldRequired"), trigger: "blur" }],
  address: [{ required: true, message: () => t("login.fieldRequired"), trigger: "blur" }],
  port: [{ required: true, message: () => t("login.fieldRequired"), trigger: "blur" }],
  api_port: [{ required: true, message: () => t("login.fieldRequired"), trigger: "blur" }],
};

watch(
  () => props.modelValue,
  (open) => {
    errorMsg.value = "";
    if (!open) return;
    if (props.node) Object.assign(form, defaultNode(), props.node);
    else Object.assign(form, defaultNode());
  }
);

const submitting = ref(false);

async function onSubmit() {
  if (!formRef.value) return;
  const valid = await formRef.value.validate().catch(() => false);
  if (!valid) return;
  errorMsg.value = "";
  submitting.value = true;
  try {
    if (isEditing.value) {
      await updateNode.mutateAsync({ ...form });
      ElMessage.success(t("nodes.editNode"));
    } else {
      await addNode.mutateAsync({ ...form });
      ElMessage.success(t("nodes.addNodeSuccess", { name: form.name }));
    }
    emit("update:modelValue", false);
  } catch (err: any) {
    const detail = err?.response?._data?.detail || err?.data?.detail;
    errorMsg.value =
      typeof detail === "string" ? detail : detail ? JSON.stringify(detail) : String(err);
  } finally {
    submitting.value = false;
  }
}
</script>

<template>
  <el-dialog
    :model-value="modelValue"
    :title="isEditing ? t('nodes.editNode') : t('nodes.addNewMarzbanNode')"
    width="520px"
    @update:model-value="(v: boolean) => emit('update:modelValue', v)"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
      <el-form-item :label="t('nodes.nodeName')" prop="name">
        <el-input v-model="form.name" />
      </el-form-item>
      <el-form-item :label="t('nodes.nodeAddress')" prop="address">
        <el-input v-model="form.address" />
      </el-form-item>
      <div class="grid-2">
        <el-form-item :label="t('nodes.nodePort')" prop="port">
          <el-input-number v-model="form.port" :min="1" :controls="false" style="width: 100%" />
        </el-form-item>
        <el-form-item :label="t('nodes.nodeAPIPort')" prop="api_port">
          <el-input-number v-model="form.api_port" :min="1" :controls="false" style="width: 100%" />
        </el-form-item>
      </div>
      <el-form-item :label="t('nodes.usageCoefficient')">
        <el-input-number v-model="form.usage_coefficient" :min="0" :step="0.1" :controls="false" style="width: 100%" />
      </el-form-item>
      <el-form-item v-if="!isEditing">
        <el-checkbox v-model="form.add_as_new_host">
          {{ t("nodes.addHostForEveryInbound") }}
        </el-checkbox>
      </el-form-item>
      <el-alert v-if="errorMsg" :title="errorMsg" type="error" :closable="false" show-icon />
    </el-form>
    <template #footer>
      <el-button @click="emit('update:modelValue', false)">{{ t("cancel") }}</el-button>
      <el-button type="primary" :loading="submitting" @click="onSubmit">
        {{ isEditing ? t("nodes.editNode") : t("nodes.addNode") }}
      </el-button>
    </template>
  </el-dialog>
</template>

<style scoped>
.grid-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
</style>
