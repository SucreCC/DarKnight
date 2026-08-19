import { defineStore } from "pinia";
import { reactive, ref } from "vue";
import {
  getUsersPerPageLimitSize,
  setUsersPerPageLimitSize,
} from "@/shared/lib/userPreferenceStorage";
import type { User, UserFilters } from "./types";

export const useUsersStore = defineStore("users", () => {
  const filters = reactive<UserFilters>({
    search: "",
    limit: getUsersPerPageLimitSize(),
    offset: 0,
    sort: "-created_at",
    status: undefined,
  });

  const editingUser = ref<User | null>(null);
  const isCreating = ref(false);
  const deletingUser = ref<User | null>(null);
  const resetUsageUser = ref<User | null>(null);
  const revokeSubUser = ref<User | null>(null);
  const isResettingAll = ref(false);
  const qrUser = ref<User | null>(null);

  function setFilters(patch: Partial<UserFilters>) {
    Object.assign(filters, patch);
  }

  function setPage(page: number) {
    filters.offset = (page - 1) * filters.limit;
  }

  function setLimit(limit: number) {
    filters.limit = limit;
    filters.offset = 0;
    setUsersPerPageLimitSize(limit);
  }

  function openCreate() {
    editingUser.value = null;
    isCreating.value = true;
  }

  function openEdit(user: User) {
    isCreating.value = false;
    editingUser.value = user;
  }

  function closeDialog() {
    isCreating.value = false;
    editingUser.value = null;
  }

  return {
    filters,
    editingUser,
    isCreating,
    deletingUser,
    resetUsageUser,
    revokeSubUser,
    isResettingAll,
    qrUser,
    setFilters,
    setPage,
    setLimit,
    openCreate,
    openEdit,
    closeDialog,
  };
});
