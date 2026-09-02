<script setup lang="ts">
import { nextTick, onMounted, onBeforeUnmount, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import { registerUser, sendVerificationCode } from '@/api/portal'
import { isEmailAlreadyRegisteredError, resolvePortalApiError } from '@/utils/portalError'
import { removeUserToken, setUserToken } from '@/utils/userAuth'
import LanguageSwitch from '@/components/LanguageSwitch/index.vue'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import SlideCaptchaDialog from './components/SlideCaptchaDialog.vue'

const { t } = useI18n()
const router = useRouter()
const route = useRoute()

const form = reactive({
  email: '',
  code: '',
  password: '',
  confirmPassword: '',
  inviteCode: ''
})
const fieldErrors = reactive({
  email: '',
  code: '',
  password: '',
  confirmPassword: ''
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

let timer: number | null = null
let clearTimers: number[] = []

const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

function unlockField(field: 'code' | 'password' | 'confirm') {
  if (field === 'code') codeReadonly.value = false
  if (field === 'password') passwordReadonly.value = false
  if (field === 'confirm') confirmReadonly.value = false
}

/** 浏览器常把邮箱误填进验证码框，发现 @ 就清掉 */
function sanitizeCodeInput() {
  if (form.code.includes('@')) {
    form.code = ''
  }
}

function purgeAutofillNoise() {
  sanitizeCodeInput()
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
  const inviteFromQuery = route.query.invite
  if (typeof inviteFromQuery === 'string' && inviteFromQuery.trim()) {
    form.inviteCode = inviteFromQuery.trim()
  }
  for (const ms of [50, 200, 500, 1000]) {
    clearTimers.push(window.setTimeout(purgeAutofillNoise, ms))
  }
})

onBeforeUnmount(() => {
  clearTimers.forEach((id) => clearTimeout(id))
  clearTimers = []
  if (timer !== null) clearInterval(timer)
})

function startCountdown() {
  countdown.value = 60
  timer = window.setInterval(() => {
    countdown.value -= 1
    if (countdown.value <= 0 && timer !== null) {
      clearInterval(timer)
      timer = null
    }
  }, 1000)
}

function validateEmailField(): boolean {
  if (!form.email.trim()) {
    fieldErrors.email = t('portal.fieldRequired')
    return false
  }
  if (!emailPattern.test(form.email.trim())) {
    fieldErrors.email = t('portal.invalidEmail')
    return false
  }
  fieldErrors.email = ''
  return true
}

function validate(): boolean {
  validateEmailField()

  fieldErrors.code = form.code.trim() ? '' : t('portal.fieldRequired')

  if (!form.password) {
    fieldErrors.password = t('portal.fieldRequired')
  } else if (form.password.length < 6) {
    fieldErrors.password = t('portal.passwordTooShort')
  } else {
    fieldErrors.password = ''
  }

  if (!form.confirmPassword) {
    fieldErrors.confirmPassword = t('portal.fieldRequired')
  } else if (form.confirmPassword !== form.password) {
    fieldErrors.confirmPassword = t('portal.passwordMismatch')
  } else {
    fieldErrors.confirmPassword = ''
  }

  return (
    !fieldErrors.email &&
    !fieldErrors.code &&
    !fieldErrors.password &&
    !fieldErrors.confirmPassword
  )
}

async function onSendCode() {
  if (sending.value || countdown.value > 0) return
  if (!validateEmailField()) return
  captchaVisible.value = true
}

async function onCaptchaSuccess() {
  errorMsg.value = ''
  sending.value = true
  try {
    await sendVerificationCode(form.email.trim())
    startCountdown()
    toast.success(t('portal.codeSent'))
    await nextTick()
    form.code = ''
    codeReadonly.value = true
  } catch (err: unknown) {
    const msg = resolvePortalApiError(err, t)
    errorMsg.value = isEmailAlreadyRegisteredError(err)
      ? t('portal.emailAlreadyRegisteredHint')
      : msg
    toast.error(msg)
  } finally {
    sending.value = false
  }
}

async function onSubmit() {
  if (!validate()) return

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
    const msg = resolvePortalApiError(err, t)
    errorMsg.value = isEmailAlreadyRegisteredError(err)
      ? t('portal.emailAlreadyRegisteredHint')
      : msg
    toast.error(msg)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="flex min-h-screen flex-col bg-muted/40 p-6">
    <div class="flex justify-end">
      <LanguageSwitch />
    </div>
    <div class="flex flex-1 items-center justify-center">
      <div class="relative w-full max-w-md rounded-xl border border-border bg-card p-7 shadow-sm">
        <h1 class="text-center text-2xl font-bold tracking-tight text-foreground">
          {{ t('portal.siteName') }}
        </h1>
        <p class="mb-6 mt-2 text-center text-sm text-muted-foreground">
          {{ t('portal.registerSubtitle') }}
        </p>

        <form class="flex flex-col gap-4" autocomplete="off" @submit.prevent="onSubmit">
          <div class="autofill-trap" aria-hidden="true">
            <input type="text" tabindex="-1" autocomplete="username" />
            <input type="password" tabindex="-1" autocomplete="current-password" />
          </div>

          <div class="space-y-2">
            <Label for="register-email">{{ t('portal.email') }}</Label>
            <Input
              id="register-email"
              v-model="form.email"
              type="email"
              name="email"
              autocomplete="email"
              :placeholder="t('portal.email')"
            />
            <p v-if="fieldErrors.email" class="text-sm text-destructive">{{ fieldErrors.email }}</p>
          </div>

          <div class="space-y-2">
            <Label for="register-code">{{ t('portal.verificationCode') }}</Label>
            <div class="flex gap-2">
              <Input
                id="register-code"
                v-model="form.code"
                class="flex-1"
                name="one_time_code"
                type="text"
                inputmode="numeric"
                maxlength="8"
                autocomplete="one-time-code"
                :readonly="codeReadonly"
                :placeholder="t('portal.verificationCode')"
                @focus="unlockField('code')"
                @input="sanitizeCodeInput"
              />
              <Button
                type="button"
                class="shrink-0"
                :disabled="sending || countdown > 0"
                @click="onSendCode"
              >
                {{ countdown > 0 ? `${countdown}s` : t('portal.sendCode') }}
              </Button>
            </div>
            <p v-if="fieldErrors.code" class="text-sm text-destructive">{{ fieldErrors.code }}</p>
          </div>

          <div class="space-y-2">
            <Label for="register-password">{{ t('portal.password') }}</Label>
            <Input
              id="register-password"
              v-model="form.password"
              type="password"
              name="new-password"
              autocomplete="new-password"
              :readonly="passwordReadonly"
              :placeholder="t('portal.password')"
              @focus="unlockField('password')"
            />
            <p v-if="fieldErrors.password" class="text-sm text-destructive">
              {{ fieldErrors.password }}
            </p>
          </div>

          <div class="space-y-2">
            <Label for="register-confirm">{{ t('portal.confirmPassword') }}</Label>
            <Input
              id="register-confirm"
              v-model="form.confirmPassword"
              type="password"
              name="confirm-new-password"
              autocomplete="new-password"
              :readonly="confirmReadonly"
              :placeholder="t('portal.confirmPassword')"
              @focus="unlockField('confirm')"
            />
            <p v-if="fieldErrors.confirmPassword" class="text-sm text-destructive">
              {{ fieldErrors.confirmPassword }}
            </p>
          </div>

          <div class="space-y-2">
            <Label for="register-invite">{{ t('portal.inviteCodeOptional') }}</Label>
            <Input
              id="register-invite"
              v-model="form.inviteCode"
              name="invite_code"
              autocomplete="off"
              :placeholder="t('portal.inviteCodeOptional')"
            />
          </div>

          <Alert v-if="errorMsg" variant="destructive">
            <AlertDescription>{{ errorMsg }}</AlertDescription>
          </Alert>

          <Button type="submit" class="h-11 w-full" :disabled="loading">
            {{ t('portal.register') }}
          </Button>
        </form>

        <div class="mt-5 border-t border-border pt-4 text-center">
          <Button variant="link" class="h-auto p-0" @click="router.push({ name: 'login' })">
            {{ t('portal.backToLogin') }}
          </Button>
        </div>
      </div>
    </div>

    <SlideCaptchaDialog v-model="captchaVisible" @success="onCaptchaSuccess" />
  </div>
</template>

<style scoped>
.autofill-trap {
  position: absolute;
  inset-inline-start: 0;
  top: 0;
  z-index: -1;
  width: 0;
  height: 0;
  overflow: hidden;
  opacity: 0;
  pointer-events: none;
}
</style>
