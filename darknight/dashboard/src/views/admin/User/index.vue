<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { toast } from 'vue-sonner'
import { useUsersStore } from '@/store/modules/user'
import { useUsersQuery, useUserMutations } from '@/api/user'
import type { User } from '@/api/user/types'
import { useConfirm } from '@/composables/useConfirm'
import UserFilters from './components/UserFilters.vue'
import UsersTable from './components/UsersTable.vue'
import UserDialog from './components/UserDialog.vue'
import QRCodeDialog from './components/QRCodeDialog.vue'
import Statistics from './components/Statistics.vue'

const { t } = useI18n()
const { confirm } = useConfirm()
const store = useUsersStore()
const { data, isFetching } = useUsersQuery(() => ({ ...store.filters }))
const { deleteUser, resetUserUsage, resetAllUsage, revokeSub } = useUserMutations()

const users = computed<User[]>(() => data.value?.users ?? [])
const total = computed(() => data.value?.total ?? 0)
const page = computed(() => Math.floor((store.filters.offset ?? 0) / store.filters.limit) + 1)

const dialogVisible = computed({
  get: () => store.isCreating || !!store.editingUser,
  set: (v: boolean) => {
    if (!v) store.closeDialog()
  }
})
const qrVisible = ref(false)

function stripHtml(text: string) {
  return text.replace(/<\/?b>/gi, '')
}

function onEdit(user: User) {
  store.openEdit(user)
}
function onQr(user: User) {
  store.qrUser = user
  qrVisible.value = true
}

async function onRemove(user: User) {
  try {
    await confirm({
      title: t('deleteUser.title'),
      description: stripHtml(t('deleteUser.prompt', { username: user.username })),
      destructive: true
    })
  } catch {
    return
  }
  try {
    await deleteUser.mutateAsync(user.username)
    toast.success(t('deleteUser.deleteSuccess', { username: user.username }))
  } catch {
    /* handled globally */
  }
}

async function onResetUsage(user: User) {
  try {
    await confirm({
      title: t('resetUserUsage.title'),
      description: stripHtml(t('resetUserUsage.prompt', { username: user.username })),
      destructive: true
    })
  } catch {
    return
  }
  try {
    await resetUserUsage.mutateAsync(user.username)
    toast.success(t('resetUserUsage.success', { username: user.username }))
  } catch {
    toast.error(t('resetUserUsage.error'))
  }
}

async function onRevokeSub(user: User) {
  try {
    await confirm({
      title: t('revokeUserSub.title'),
      description: stripHtml(t('revokeUserSub.prompt', { username: user.username })),
      destructive: true
    })
  } catch {
    return
  }
  try {
    await revokeSub.mutateAsync(user.username)
    toast.success(t('revokeUserSub.success', { username: user.username }))
  } catch {
    toast.error(t('revokeUserSub.error'))
  }
}

async function onResetAll() {
  try {
    await confirm({
      title: t('resetAllUsage.title'),
      description: t('resetAllUsage.prompt'),
      destructive: true
    })
  } catch {
    return
  }
  try {
    await resetAllUsage.mutateAsync()
    toast.success(t('resetAllUsage.success'))
  } catch {
    toast.error(t('resetAllUsage.error'))
  }
}
</script>

<template>
  <div class="flex max-w-6xl flex-col gap-4">
    <Statistics />

    <UserFilters
      :search="store.filters.search ?? ''"
      :status="store.filters.status"
      @update:search="(v) => store.setFilters({ search: v, offset: 0 })"
      @update:status="(v) => store.setFilters({ status: v, offset: 0 })"
      @create="store.openCreate()"
      @reset-all="onResetAll"
    />

    <UsersTable
      :users="users"
      :total="total"
      :loading="isFetching"
      :page="page"
      :limit="store.filters.limit"
      @edit="onEdit"
      @qr="onQr"
      @remove="onRemove"
      @update:page="store.setPage"
      @update:limit="store.setLimit"
    />

    <UserDialog
      v-model="dialogVisible"
      :user="store.editingUser"
      @reset-usage="onResetUsage"
      @revoke-sub="onRevokeSub"
    />

    <QRCodeDialog v-model="qrVisible" :user="store.qrUser" />
  </div>
</template>
