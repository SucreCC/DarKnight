<script setup lang="ts">
import { computed, reactive, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { AlertTriangle } from 'lucide-vue-next'
import { toast } from 'vue-sonner'
import {
  changePortalPassword,
  fetchPortalProfile,
  revokePortalSubscription,
  updatePortalProfile
} from '@/api/portal/profile'
import { resolvePortalApiError } from '@/utils/portalError'
import { Alert, AlertDescription } from '@/components/ui/alert'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger
} from '@/components/ui/alert-dialog'
import { Button } from '@/components/ui/button'
import { PasswordInput } from '@/components/ui/password-input'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'

const { t } = useI18n()
const queryClient = useQueryClient()

const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})
const passwordErrors = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const profileQuery = useQuery({
  queryKey: ['portal', 'profile'],
  queryFn: fetchPortalProfile,
  refetchOnWindowFocus: false
})

const profile = computed(() => profileQuery.data.value)

async function patchProfile(
  body: Partial<{ notify_expire_email: boolean; notify_traffic_email: boolean }>
) {
  try {
    await updatePortalProfile(body)
    queryClient.invalidateQueries({ queryKey: ['portal', 'profile'] })
  } catch (err) {
    toast.error(resolvePortalApiError(err, t))
    queryClient.invalidateQueries({ queryKey: ['portal', 'profile'] })
  }
}

function onNotifyExpireChange(value: boolean) {
  patchProfile({ notify_expire_email: value })
}

function onNotifyTrafficChange(value: boolean) {
  patchProfile({ notify_traffic_email: value })
}

function syncConfirmPasswordError() {
  if (!passwordForm.confirmPassword) {
    passwordErrors.confirmPassword = ''
    return
  }
  passwordErrors.confirmPassword =
    passwordForm.confirmPassword === passwordForm.newPassword ? '' : t('portal.passwordMismatch')
}

watch(() => passwordForm.newPassword, syncConfirmPasswordError)
watch(() => passwordForm.confirmPassword, syncConfirmPasswordError)

function validatePasswordForm(): boolean {
  passwordErrors.oldPassword = passwordForm.oldPassword ? '' : t('portal.fieldRequired')
  if (!passwordForm.newPassword) {
    passwordErrors.newPassword = t('portal.fieldRequired')
  } else if (passwordForm.newPassword.length < 6) {
    passwordErrors.newPassword = t('portal.passwordTooShort')
  } else {
    passwordErrors.newPassword = ''
  }
  if (!passwordForm.confirmPassword) {
    passwordErrors.confirmPassword = t('portal.fieldRequired')
  } else if (passwordForm.confirmPassword !== passwordForm.newPassword) {
    passwordErrors.confirmPassword = t('portal.passwordMismatch')
  } else {
    passwordErrors.confirmPassword = ''
  }
  return !passwordErrors.oldPassword && !passwordErrors.newPassword && !passwordErrors.confirmPassword
}

const passwordMutation = useMutation({
  mutationFn: () =>
    changePortalPassword({
      old_password: passwordForm.oldPassword,
      new_password: passwordForm.newPassword
    }),
  onSuccess: () => {
    passwordForm.oldPassword = ''
    passwordForm.newPassword = ''
    passwordForm.confirmPassword = ''
    toast.success(t('portal.profile.passwordUpdated'), { id: 'change-password' })
  },
  onError: (err) => {
    toast.error(resolvePortalApiError(err, t), { id: 'change-password' })
  }
})

function onSavePassword() {
  if (!validatePasswordForm()) return
  passwordMutation.mutate()
}

const revokeMutation = useMutation({
  mutationFn: revokePortalSubscription,
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['portal', 'me'] })
    toast.success(t('portal.profile.resetSubSuccess'), { id: 'reset-sub' })
  },
  onError: (err) => {
    toast.error(resolvePortalApiError(err, t), { id: 'reset-sub' })
  }
})
</script>

<template>
  <div class="flex max-w-6xl flex-col gap-5">
    <Alert v-if="profileQuery.isError.value" variant="destructive">
      <AlertDescription>{{ t('portal.requestFailed') }}</AlertDescription>
    </Alert>

    <!-- 修改密码 -->
    <div class="rounded-2xl border border-slate-200/80 bg-card p-6 shadow-sm dark:border-border">
      <h2 class="mb-4 text-base font-semibold text-foreground">{{ t('portal.profile.changePassword') }}</h2>
      <div class="flex max-w-md flex-col gap-4">
        <div class="space-y-2">
          <Label for="profile-old-password">{{ t('portal.profile.oldPassword') }}</Label>
          <PasswordInput
            id="profile-old-password"
            v-model="passwordForm.oldPassword"
            autocomplete="current-password"
            class="bg-slate-50 dark:bg-muted/40"
          />
          <p v-if="passwordErrors.oldPassword" class="text-sm text-destructive">
            {{ passwordErrors.oldPassword }}
          </p>
        </div>
        <div class="space-y-2">
          <Label for="profile-new-password">{{ t('portal.profile.newPassword') }}</Label>
          <PasswordInput
            id="profile-new-password"
            v-model="passwordForm.newPassword"
            autocomplete="new-password"
            :placeholder="t('portal.profile.newPasswordPlaceholder')"
          />
          <p v-if="passwordErrors.newPassword" class="text-sm text-destructive">
            {{ passwordErrors.newPassword }}
          </p>
        </div>
        <div class="space-y-2">
          <Label for="profile-confirm-password">{{ t('portal.confirmPassword') }}</Label>
          <PasswordInput
            id="profile-confirm-password"
            v-model="passwordForm.confirmPassword"
            autocomplete="new-password"
            :placeholder="t('portal.profile.newPasswordPlaceholder')"
            :aria-invalid="passwordErrors.confirmPassword ? true : undefined"
          />
          <p v-if="passwordErrors.confirmPassword" class="text-sm text-destructive">
            {{ passwordErrors.confirmPassword }}
          </p>
        </div>
        <Button
          class="w-fit"
          :disabled="passwordMutation.isPending.value"
          @click="onSavePassword"
        >
          {{ t('portal.profile.save') }}
        </Button>
      </div>
    </div>

    <!-- 通知 -->
    <div class="overflow-hidden rounded-2xl border border-slate-200/80 bg-card shadow-sm dark:border-border">
      <div class="border-b border-border bg-slate-50 px-6 py-3 dark:bg-muted/30">
        <h2 class="text-base font-semibold text-foreground">{{ t('portal.profile.notifications') }}</h2>
      </div>
      <div class="divide-y divide-border px-6 py-2">
        <div class="flex flex-col gap-2 py-4 sm:flex-row sm:items-center sm:justify-between">
          <span class="text-sm text-foreground">{{ t('portal.profile.notifyExpire') }}</span>
          <Switch
            :model-value="profile?.notify_expire_email ?? true"
            @update:model-value="onNotifyExpireChange"
          />
        </div>
        <div class="flex flex-col gap-2 py-4 sm:flex-row sm:items-center sm:justify-between">
          <span class="text-sm text-foreground">{{ t('portal.profile.notifyTraffic') }}</span>
          <Switch
            :model-value="profile?.notify_traffic_email ?? true"
            @update:model-value="onNotifyTrafficChange"
          />
        </div>
      </div>
    </div>

    <!-- 重置订阅 -->
    <div class="rounded-2xl border border-slate-200/80 bg-card p-6 shadow-sm dark:border-border">
      <h2 class="mb-4 text-base font-semibold text-foreground">
        {{ t('portal.profile.resetSubscription') }}
      </h2>
      <Alert class="mb-4 border-amber-200 bg-amber-50 text-amber-900 dark:border-amber-900/40 dark:bg-amber-950/30 dark:text-amber-100">
        <AlertTriangle class="size-4" />
        <AlertDescription>{{ t('portal.profile.resetSubscriptionHint') }}</AlertDescription>
      </Alert>
      <AlertDialog>
        <AlertDialogTrigger as-child>
          <Button variant="destructive">{{ t('portal.profile.reset') }}</Button>
        </AlertDialogTrigger>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>{{ t('portal.profile.resetConfirmTitle') }}</AlertDialogTitle>
            <AlertDialogDescription>{{ t('portal.profile.resetConfirmDesc') }}</AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>{{ t('cancel') }}</AlertDialogCancel>
            <AlertDialogAction
              class="bg-destructive text-destructive-foreground hover:bg-destructive/90"
              :disabled="revokeMutation.isPending.value"
              @click="revokeMutation.mutate()"
            >
              {{ t('portal.profile.reset') }}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  </div>
</template>
