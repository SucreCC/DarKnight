<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import type { FormInstance, FormRules } from 'element-plus'
import { extractErrorDetail } from '@/config/axios'
import { registerUser, sendVerificationCode } from '@/api/portal'
import { removeUserToken, setUserToken } from '@/utils/userAuth'
import LanguageSwitch from '@/components/LanguageSwitch/index.vue'

const { t } = useI18n()
const router = useRouter()

const formRef = ref<FormInstance>()
const form = reactive({
  email: '',
  code: '',
  password: '',
  confirmPassword: '',
  inviteCode: ''
})
const loading = ref(false)
const sending = ref(false)
const countdown = ref(0)
const errorMsg = ref('')

let timer: ReturnType<typeof setInterval> | null = null

const rules: FormRules = {
  email: [
    { required: true, message: () => t('portal.fieldRequired'), trigger: 'blur' },
    { type: 'email', message: () => t('portal.invalidEmail'), trigger: 'blur' }
  ],
  code: [{ required: true, message: () => t('portal.fieldRequired'), trigger: 'blur' }],
  password: [
    { required: true, message: () => t('portal.fieldRequired'), trigger: 'blur' },
    { min: 6, message: () => t('portal.passwordTooShort'), trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: () => t('portal.fieldRequired'), trigger: 'blur' },
    {
      validator: (_rule, value, callback) => {
        if (value !== form.password) callback(new Error(t('portal.passwordMismatch')))
        else callback()
      },
      trigger: 'blur'
    }
  ]
}

onMounted(() => {
  removeUserToken()
})

function startCountdown() {
  countdown.value = 60
  timer = setInterval(() => {
    countdown.value -= 1
    if (countdown.value <= 0 && timer) {
      clearInterval(timer)
      timer = null
    }
  }, 1000)
}

async function onSendCode() {
  if (!form.email.trim()) {
    errorMsg.value = t('portal.emailRequiredFirst')
    return
  }
  errorMsg.value = ''
  sending.value = true
  try {
    await sendVerificationCode(form.email.trim())
    startCountdown()
  } catch (err: unknown) {
    const detail = extractErrorDetail(err)
    errorMsg.value = typeof detail === 'string' ? detail : String(err)
  } finally {
    sending.value = false
  }
}

async function onSubmit() {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  errorMsg.value = ''
  loading.value = true
  try {
    const res = await registerUser({
      email: form.email.trim(),
      code: form.code.trim(),
      password: form.password,
      invite_code: form.inviteCode.trim() || undefined
    })
    setUserToken(res.access_token)
    router.push({ name: 'portal-dashboard' })
  } catch (err: unknown) {
    const detail = extractErrorDetail(err)
    errorMsg.value = typeof detail === 'string' ? detail : String(err)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="portal-auth-page">
    <div class="portal-auth-topbar">
      <LanguageSwitch />
    </div>
    <div class="portal-auth-center">
      <div class="portal-auth-card">
        <h1 class="portal-auth-title">{{ t('portal.siteName') }}</h1>
        <p class="portal-auth-sub">{{ t('portal.registerSubtitle') }}</p>
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
          <el-form-item prop="code">
            <div class="code-row">
              <el-input
                v-model="form.code"
                :placeholder="t('portal.verificationCode')"
                size="large"
              />
              <el-button
                type="primary"
                size="large"
                class="send-btn"
                :loading="sending"
                :disabled="countdown > 0"
                @click="onSendCode"
              >
                {{ countdown > 0 ? `${countdown}s` : t('portal.sendCode') }}
              </el-button>
            </div>
          </el-form-item>
          <el-form-item prop="password">
            <el-input
              v-model="form.password"
              type="password"
              show-password
              :placeholder="t('portal.password')"
              size="large"
            />
          </el-form-item>
          <el-form-item prop="confirmPassword">
            <el-input
              v-model="form.confirmPassword"
              type="password"
              show-password
              :placeholder="t('portal.confirmPassword')"
              size="large"
            />
          </el-form-item>
          <el-form-item>
            <el-input
              v-model="form.inviteCode"
              :placeholder="t('portal.inviteCodeOptional')"
              size="large"
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
            {{ t('portal.register') }}
          </el-button>
        </el-form>
        <div class="portal-auth-footer">
          <router-link :to="{ name: 'login' }">{{ t('portal.backToLogin') }}</router-link>
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

.code-row {
  display: flex;
  width: 100%;
  gap: 12px;
}

.code-row .el-input {
  flex: 1;
}

.send-btn {
  flex-shrink: 0;
  --el-button-bg-color: #20a397;
  --el-button-border-color: #20a397;
  --el-button-hover-bg-color: #1b8f84;
  --el-button-hover-border-color: #1b8f84;
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
