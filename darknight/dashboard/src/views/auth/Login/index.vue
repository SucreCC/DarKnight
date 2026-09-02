<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { extractErrorDetail } from '@/config/axios'
import { loginAccount } from '@/api/portal'
import { removeToken, setToken } from '@/utils/auth'
import { removeUserToken, setUserToken } from '@/utils/userAuth'
import LanguageSwitch from '@/components/LanguageSwitch/index.vue'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { PasswordInput } from '@/components/ui/password-input'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

const { t } = useI18n()
const router = useRouter()
const route = useRoute()

const form = reactive({ username: '', password: '' })
const fieldErrors = reactive({ username: '', password: '' })
const loading = ref(false)
const errorMsg = ref('')

onMounted(() => {
  removeToken()
  removeUserToken()
})

function resolveRedirect(access: string): string {
  const requested = (route.query.redirect as string) || ''
  const isUser = access === 'user'
  const fallback = isUser ? '/portal/dashboard' : '/admin/users'
  if (!requested) return fallback
  if (isUser && !requested.startsWith('/portal')) return fallback
  if (!isUser && requested.startsWith('/portal')) return fallback
  if (isUser && requested.startsWith('/admin')) return fallback
  return requested
}

function goRegister() {
  router.push({ name: 'portal-register' })
}

function validate(): boolean {
  fieldErrors.username = form.username.trim() ? '' : t('login.fieldRequired')
  fieldErrors.password = form.password ? '' : t('login.fieldRequired')
  return !fieldErrors.username && !fieldErrors.password
}

async function onSubmit() {
  if (!validate()) return

  errorMsg.value = ''
  loading.value = true
  try {
    const res = await loginAccount(form.username.trim(), form.password)
    const access = res.access ?? 'user'
    if (access === 'user') {
      setUserToken(res.access_token)
      removeToken()
    } else {
      setToken(res.access_token)
      removeUserToken()
    }
    router.push(resolveRedirect(access))
  } catch (err: unknown) {
    const detail = extractErrorDetail(err)
    errorMsg.value = typeof detail === 'string' ? detail : String(err)
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
      <div class="w-full max-w-sm rounded-xl border border-border bg-card p-7 shadow-sm">
        <div class="mb-3 flex justify-center">
          <img
            src="/statics/logo.png"
            alt="DarKnight VPN"
            class="size-28 rounded-2xl object-contain"
          />
        </div>
        <h1 class="text-center text-lg font-semibold text-foreground">
          {{ t('login.loginYourAccount') }}
        </h1>
        <p class="mb-5 text-center text-sm text-muted-foreground">
          {{ t('login.welcomeBack') }}
        </p>
        <form class="flex flex-col gap-4" @submit.prevent="onSubmit">
          <div class="space-y-2">
            <Label for="login-username">{{ t('login.accountPlaceholder') }}</Label>
            <Input
              id="login-username"
              v-model="form.username"
              :placeholder="t('login.accountPlaceholder')"
              autocomplete="username"
            />
            <p v-if="fieldErrors.username" class="text-sm text-destructive">
              {{ fieldErrors.username }}
            </p>
          </div>
          <div class="space-y-2">
            <Label for="login-password">{{ t('password') }}</Label>
            <PasswordInput
              id="login-password"
              v-model="form.password"
              :placeholder="t('password')"
              autocomplete="current-password"
            />
            <p v-if="fieldErrors.password" class="text-sm text-destructive">
              {{ fieldErrors.password }}
            </p>
          </div>
          <Alert v-if="errorMsg" variant="destructive">
            <AlertDescription>{{ errorMsg }}</AlertDescription>
          </Alert>
          <Button type="submit" class="h-11 w-full" :disabled="loading">
            {{ t('login') }}
          </Button>
        </form>
        <div class="mt-4 text-center">
          <Button variant="link" class="h-auto p-0" @click="goRegister">
            {{ t('portal.goRegister') }}
          </Button>
        </div>
      </div>
    </div>
  </div>
</template>
