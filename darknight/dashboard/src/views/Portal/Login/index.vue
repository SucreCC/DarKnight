<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import type { FormInstance, FormRules } from 'element-plus'
import { extractErrorDetail } from '@/config/axios'
import { loginUser } from '@/api/portal'
import { removeUserToken, setUserToken } from '@/utils/userAuth'
import LanguageSwitch from '@/components/LanguageSwitch/index.vue'

const { t } = useI18n()
const router = useRouter()
const route = useRoute()

const formRef = ref<FormInstance>()
const form = reactive({ email: '', password: '' })
const loading = ref(false)
const errorMsg = ref('')

const rules: FormRules = {
  email: [
    { required: true, message: () => t('portal.fieldRequired'), trigger: 'blur' },
    { type: 'email', message: () => t('portal.invalidEmail'), trigger: 'blur' }
  ],
  password: [{ required: true, message: () => t('portal.fieldRequired'), trigger: 'blur' }]
}

onMounted(() => {
  removeUserToken()
})

async function onSubmit() {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  errorMsg.value = ''
  loading.value = true
  try {
    const res = await loginUser(form.email.trim(), form.password)
    setUserToken(res.access_token)
    const redirect = (route.query.redirect as string) || '/portal/dashboard'
    router.push(redirect)
  } catch (err: unknown) {
    const detail = extractErrorDetail(err)
    errorMsg.value = typeof detail === 'string' ? detail : String(err)
  } finally {
    loading.value = false
  }
}

const pageTitle = computed(() => t('portal.siteName'))
</script>

<template>
  <div class="portal-auth-page">
    <div class="portal-auth-topbar">
      <LanguageSwitch />
    </div>
    <div class="portal-auth-center">
      <div class="portal-auth-card">
        <h1 class="portal-auth-title">{{ pageTitle }}</h1>
        <p class="portal-auth-sub">{{ t('portal.loginSubtitle') }}</p>
        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          label-position="top"
          @submit.prevent="onSubmit"
        >
          <el-form-item prop="email">
            <el-input
              v-model="form.email"
              type="email"
              :placeholder="t('portal.email')"
              size="large"
            />
          </el-form-item>
          <el-form-item prop="password">
            <el-input
              v-model="form.password"
              type="password"
              show-password
              :placeholder="t('portal.password')"
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
            class="portal-auth-alert"
          />
          <el-button
            type="primary"
            size="large"
            class="portal-primary-btn"
            :loading="loading"
            @click="onSubmit"
          >
            {{ t('portal.login') }}
          </el-button>
        </el-form>
        <div class="portal-auth-footer">
          <router-link :to="{ name: 'portal-register' }">{{ t('portal.goRegister') }}</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.portal-auth-page {
  display: flex;
  min-height: 100vh;
  padding: 24px;
  flex-direction: column;
  background: #eef2f6;
}

.portal-auth-topbar {
  display: flex;
  justify-content: flex-end;
}

.portal-auth-center {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.portal-auth-card {
  width: 420px;
  padding: 32px 28px 24px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgb(0 0 0 / 6%);
}

.portal-auth-title {
  margin: 0;
  font-size: 28px;
  font-weight: 700;
  text-align: center;
  color: #303133;
}

.portal-auth-sub {
  margin: 8px 0 24px;
  color: #909399;
  text-align: center;
}

.portal-auth-alert {
  margin-bottom: 12px;
}

.portal-primary-btn {
  width: 100%;
  --el-button-bg-color: #20a397;
  --el-button-border-color: #20a397;
  --el-button-hover-bg-color: #1b8f84;
  --el-button-hover-border-color: #1b8f84;
  --el-button-active-bg-color: #187a71;
  --el-button-active-border-color: #187a71;
}

.portal-auth-footer {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
  text-align: center;
}

.portal-auth-footer a {
  color: #20a397;
  text-decoration: none;
}

:deep(.el-input__wrapper) {
  background: #f5f7fa;
  box-shadow: none;
}
</style>
