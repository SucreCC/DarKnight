<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import type { FormInstance, FormRules } from 'element-plus'
import { extractErrorDetail } from '@/config/axios'
import { loginAccount } from '@/api/portal'
import { removeToken, setToken } from '@/utils/auth'
import { removeUserToken, setUserToken } from '@/utils/userAuth'
import LanguageSwitch from '@/components/LanguageSwitch/index.vue'

const { t } = useI18n()
const router = useRouter()
const route = useRoute()

const formRef = ref<FormInstance>()
const form = reactive({ username: '', password: '' })
const loading = ref(false)
const errorMsg = ref('')

const rules: FormRules = {
  username: [{ required: true, message: () => t('login.fieldRequired'), trigger: 'blur' }],
  password: [{ required: true, message: () => t('login.fieldRequired'), trigger: 'blur' }]
}

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

async function onSubmit() {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

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
  <div class="login-page">
    <div class="login-topbar">
      <LanguageSwitch />
    </div>
    <div class="login-center">
      <el-card class="login-card">
        <div class="login-logo-wrap">
          <img src="/statics/logo.png" class="login-logo" alt="DarKnight VPN" />
        </div>
        <div class="login-heading">{{ t('login.loginYourAccount') }}</div>
        <div class="login-sub">{{ t('login.welcomeBack') }}</div>
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
              :placeholder="t('login.accountPlaceholder')"
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
            {{ t('login') }}
          </el-button>
        </el-form>
        <div class="login-portal-link">
          <el-button link type="primary" @click="goRegister">{{ t('portal.goRegister') }}</el-button>
        </div>
      </el-card>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  display: flex;
  min-height: 100vh;
  padding: 24px;
  flex-direction: column;
}

.login-topbar {
  display: flex;
  justify-content: flex-end;
}

.login-center {
  display: flex;
  flex: 1;
  align-items: center;
  justify-content: center;
}

.login-card {
  width: 360px;
}

.login-logo-wrap {
  display: flex;
  justify-content: center;
  margin-bottom: 12px;
}

.login-logo {
  width: 120px;
  height: 120px;
  object-fit: contain;
  border-radius: 16px;
}

.login-heading {
  font-size: 18px;
  font-weight: 600;
  text-align: center;
}

.login-sub {
  margin-bottom: 20px;
  color: var(--el-text-color-secondary);
  text-align: center;
}

.login-portal-link {
  margin-top: 16px;
  text-align: center;
}

.login-portal-link .el-button {
  font-size: 14px;
  color: #20a397;
}
</style>
