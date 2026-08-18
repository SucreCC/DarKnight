<script setup lang="ts">
import { computed, ref } from "vue";
import { useI18n } from "vue-i18n";
import { ElMessage, ElMessageBox } from "element-plus";
import { useUsersStore } from "@/features/users/store";
import { useUsersQuery, useUserMutations } from "@/features/users/api";
import type { User } from "@/features/users/types";
import UserFilters from "@/features/users/components/UserFilters.vue";
import UsersTable from "@/features/users/components/UsersTable.vue";
import UserDialog from "@/features/users/dialogs/UserDialog.vue";
import QRCodeDialog from "@/features/users/dialogs/QRCodeDialog.vue";
import Statistics from "@/components/Statistics.vue";

const { t } = useI18n();
const store = useUsersStore();
const { data, isFetching } = useUsersQuery(() => ({ ...store.filters }));
const { deleteUser, resetUserUsage, resetAllUsage, revokeSub } =
  useUserMutations();

const users = computed<User[]>(() => data.value?.users ?? []);
const total = computed(() => data.value?.total ?? 0);
const page = computed(() => Math.floor((store.filters.offset ?? 0) / store.filters.limit) + 1);

const dialogVisible = computed({
  get: () => store.isCreating || !!store.editingUser,
  set: (v: boolean) => {
    if (!v) store.closeDialog();
  },
});
const qrVisible = ref(false);

function onEdit(user: User) {
  store.openEdit(user);
}
function onQr(user: User) {
  store.qrUser = user;
  qrVisible.value = true;
}

async function onRemove(user: User) {
  await ElMessageBox.confirm(
    t("deleteUser.prompt", { username: user.username }),
    t("deleteUser.title"),
    { type: "warning", dangerouslyUseHTMLString: true }
  ).catch(() => "cancel");
  try {
    await deleteUser.mutateAsync(user.username);
    ElMessage.success(t("deleteUser.deleteSuccess", { username: user.username }));
  } catch {
    /* handled globally */
  }
}

async function onResetUsage(user: User) {
  const confirmed = await ElMessageBox.confirm(
    t("resetUserUsage.prompt", { username: user.username }),
    t("resetUserUsage.title"),
    { type: "warning", dangerouslyUseHTMLString: true }
  )
    .then(() => true)
    .catch(() => false);
  if (!confirmed) return;
  try {
    await resetUserUsage.mutateAsync(user.username);
    ElMessage.success(t("resetUserUsage.success", { username: user.username }));
  } catch {
    ElMessage.error(t("resetUserUsage.error"));
  }
}

async function onRevokeSub(user: User) {
  const confirmed = await ElMessageBox.confirm(
    t("revokeUserSub.prompt", { username: user.username }),
    t("revokeUserSub.title"),
    { type: "warning", dangerouslyUseHTMLString: true }
  )
    .then(() => true)
    .catch(() => false);
  if (!confirmed) return;
  try {
    await revokeSub.mutateAsync(user.username);
    ElMessage.success(t("revokeUserSub.success", { username: user.username }));
  } catch {
    ElMessage.error(t("revokeUserSub.error"));
  }
}

async function onResetAll() {
  const confirmed = await ElMessageBox.confirm(
    t("resetAllUsage.prompt"),
    t("resetAllUsage.title"),
    { type: "warning" }
  )
    .then(() => true)
    .catch(() => false);
  if (!confirmed) return;
  try {
    await resetAllUsage.mutateAsync();
    ElMessage.success(t("resetAllUsage.success"));
  } catch {
    ElMessage.error(t("resetAllUsage.error"));
  }
}
</script>

<template>
  <div class="dk-page">
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
