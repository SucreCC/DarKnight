<script setup lang="ts">
import { nextTick, onMounted, onBeforeUnmount, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { extractErrorDetail } from '@/config/axios'
import { registerUser, sendVerificationCode } from '@/api/portal'
import { removeUserToken, setUserToken } from '@/utils/userAuth'
import LanguageSwitch from '@/components/LanguageSwitch/index.vue'
import SlideCaptchaDialog from './components/SlideCaptchaDialog.vue'

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
const captchaVisible = ref(false)

/** 未聚焦前只读，阻止浏览器把邮箱/密码灌进验证码框 */
const codeReadonly = ref(true)
const passwordReadonly = ref(true)
const confirmReadonly = ref(true)

let timer: ReturnType<typeof setInterval> | null = null
let clearTimers: ReturnType<typeof setTimeout>[] = []

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

function unlockField(field: 'code' | 'password' | 'confirm') {
  if (field === 'code') codeReadonly.value = false
  if (field === 'password') passwordReadonly.value = false
  if (field === 'confirm') confirmReadonly.value = false
}

/** 浏览器常把邮箱误填进验证码框，发现 @ 就清掉 */
function sanitizeCodeInput() {
  // 浏览器误把邮箱填进验证码框时清掉
  if (form.code.includes('@')) {
    form.code = ''
  }
}

function purgeAutofillNoise() {
  sanitizeCodeInput()
  // 页面刚打开时密码框若被自动填充且邮箱为空，视为误填
  if (!form.email && form.password) {
    form.password = ''
    form.confirmPassword = ''
  }
}

onMounted(() => {
  removeUserToken()
  form.code = ''
  form.password = ''
  form.confirmPassword = ''
  // Chrome 自动填充是异步的，延迟再清几次
  for (const ms of [50, 200, 500, 1000]) {
    clearTimers.push(window.setTimeout(purgeAutofillNoise, ms))
  }
})

onBeforeUnmount(() => {
  clearTimers.forEach((id) => clearTimeout(id))
  clearTimers = []
  if (timer) clearInterval(timer)
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
  if (!formRef.value || sending.value || countdown.value > 0) return
  const emailOk = await formRef.value.validateField('email').then(
    () => true,
    () => false
  )
  if (!emailOk) return
  captchaVisible.value = true
}

async function onCaptchaSuccess() {
  errorMsg.value = ''
  sending.value = true
  try {
    await sendVerificationCode(form.email.trim())
    startCountdown()
    ElMessage.success(t('portal.codeSent'))
    await nextTick()
    form.code = ''
    codeReadonly.value = true
  } catch (err: unknown) {
    const detail = extractErrorDetail(err)
    const msg = typeof detail === 'string' ? detail : String(err)
    errorMsg.value = msg
    ElMessage.error(msg)
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
          autocomplete="off"
          @submit.prevent="onSubmit"
        >
          <!-- 诱饵字段：吸收浏览器自动填充，避免灌进验证码/密码框 -->
          <div class="autofill-trap" aria-hidden="true">
            <input type="text" tabindex="-1" autocomplete="username" />
            <input type="password" tabindex="-1" autocomplete="current-password" />
          </div>

          <el-form-item prop="email">
            <el-input
              v-model="form.email"
              type="email"
              name="email"
              autocomplete="email"
              :placeholder="t('portal.email')"
              size="large"
            />
          </el-form-item>
          <el-form-item prop="code">
            <div class="code-row">
              <el-input
                v-model="form.code"
                name="one_time_code"
                type="text"
                inputmode="numeric"
                maxlength="8"
                autocomplete="one-time-code"
                :readonly="codeReadonly"
                :placeholder="t('portal.verificationCode')"
                size="large"
                @focus="unlockField('code')"
                @input="sanitizeCodeInput"
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
              name="new-password"
              autocomplete="new-password"
              :readonly="passwordReadonly"
              show-password
              :placeholder="t('portal.password')"
              size="large"
              @focus="unlockField('password')"
            />
          </el-form-item>
          <el-form-item prop="confirmPassword">
            <el-input
              v-model="form.confirmPassword"
              type="password"
              name="confirm-new-password"
              autocomplete="new-password"
              :readonly="confirmReadonly"
              show-password
              :placeholder="t('portal.confirmPassword')"
              size="large"
              @focus="unlockField('confirm')"
            />
          </el-form-item>
          <el-form-item>
            <el-input
              v-model="form.inviteCode"
              name="invite_code"
              autocomplete="off"
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
          <el-button link type="primary" @click="router.push({ name: 'login' })">
            {{ t('portal.backToLogin') }}
          </el-button>
        </div>
      </div>
    </div>

    <SlideCaptchaDialog v-model="captchaVisible" @success="onCaptchaSuccess" />
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

.autofill-trap {
  position: absolute;
  top: 0;
  left: 0;
  z-index: -1;
  width: 0;
  height: 0;
  overflow: hidden;
  opacity: 0;
  pointer-events: none;
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

/* 盖掉 Chrome 自动填充的浅蓝色底 */
:deep(input.el-input__inner:-webkit-autofill),
:deep(input.el-input__inner:-webkit-autofill:hover),
:deep(input.el-input__inner:-webkit-autofill:focus),
:deep(input.el-input__inner:-webkit-autofill:active) {
  -webkit-text-fill-color: #303133 !important;
  caret-color: #303133;
  transition: background-color 99999s ease-out;
  box-shadow: 0 0 0 1000px #f5f7fa inset !important;
}
</style>
