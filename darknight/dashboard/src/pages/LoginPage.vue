<script setup lang="ts">
import { onMounted, reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useI18n } from "vue-i18n";
import type { FormInstance, FormRules } from "element-plus";
import { http } from "@/shared/api/http";
import { removeAuthToken, setAuthToken } from "@/shared/lib/authStorage";
import LanguageSwitch from "@/components/LanguageSwitch.vue";

const { t } = useI18n();
const router = useRouter();
const route = useRoute();

const formRef = ref<FormInstance>();
const form = reactive({ username: "", password: "" });
const loading = ref(false);
const errorMsg = ref("");

const rules: FormRules = {
  username: [{ required: true, message: () => t("login.fieldRequired"), trigger: "blur" }],
  password: [{ required: true, message: () => t("login.fieldRequired"), trigger: "blur" }],
};

onMounted(() => {
  removeAuthToken();
});

async function onSubmit() {
  if (!formRef.value) return;
  const valid = await formRef.value.validate().catch(() => false);
  if (!valid) return;

  errorMsg.value = "";
  loading.value = true;
  const formData = new FormData();
  formData.append("username", form.username);
  formData.append("password", form.password);
  formData.append("grant_type", "password");
  try {
    const res = await http<{ access_token: string }>("/admin/token", {
      method: "POST",
      body: formData,
    });
    setAuthToken(res.access_token);
    const redirect = (route.query.redirect as string) || "/";
    router.push(redirect);
  } catch (err: any) {
    errorMsg.value =
      err?.response?._data?.detail || err?.data?.detail || String(err);
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="login-page">
    <div class="login-topbar">
      <LanguageSwitch />
    </div>
    <div class="login-center">
      <el-card class="login-card">
        <div class="login-title">DarKnight</div>
        <div class="login-heading">{{ t("login.loginYourAccount") }}</div>
        <div class="login-sub">{{ t("login.welcomeBack") }}</div>
        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          label-position="top"
          @submit.prevent="onSubmit"
        >
          <el-form-item prop="username">
            <el-input
              v-model="form.username"
              :placeholder="t('username')"
              size="large"
            />
          </el-form-item>
          <el-form-item prop="password">
            <el-input
              v-model="form.password"
              type="password"
              show-password
              :placeholder="t('password')"
              size="large"
              @keyup.enter="onSubmit"
            />
          </el-form-item>
          <el-alert
            v-if="errorMsg"
            :title="errorMsg"
            type="error"
            :closable="false"
            show-icon
            style="margin-bottom: 12px"
          />
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            style="width: 100%"
            @click="onSubmit"
          >
            {{ t("login") }}
          </el-button>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  padding: 24px;
}
.login-topbar {
  display: flex;
  justify-content: flex-end;
}
.login-center {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}
.login-card {
  width: 360px;
}
.login-title {
  font-size: 28px;
  font-weight: 700;
  text-align: center;
  margin-bottom: 8px;
}
.login-heading {
  font-size: 18px;
  font-weight: 600;
  text-align: center;
}
.login-sub {
  color: var(--el-text-color-secondary);
  text-align: center;
  margin-bottom: 20px;
}
</style>
