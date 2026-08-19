<script setup lang="ts">
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import {
  CopyDocument,
  Delete,
  Edit,
  Link as LinkIcon,
  Pointer,
} from "@element-plus/icons-vue";
import { ElMessage } from "element-plus";
import { formatBytes } from "@/shared/lib/format";
import { relativeExpiry, isExpired } from "@/shared/lib/date";
import { STATUS_TAG_TYPE, type User } from "./types";
import {
  absoluteSubscriptionUrl,
  isUnlimited,
  usagePercentage,
  usageTotalText,
} from "./helpers";

const props = defineProps<{
  users: User[];
  total: number;
  loading: boolean;
  page: number;
  limit: number;
}>();

const emit = defineEmits<{
  edit: [user: User];
  qr: [user: User];
  remove: [user: User];
  "update:page": [page: number];
  "update:limit": [limit: number];
}>();

const { t } = useI18n();

const asUser = (row: unknown): User => row as User;

const statusTagType = (status: User["status"]) =>
  STATUS_TAG_TYPE[status] ?? "info";

function expiryText(user: User): string {
  if (!user.expire) return "";
  const rel = relativeExpiry(user.expire);
  if (!rel) return "";
  return isExpired(user.expire)
    ? t("expired", { time: rel })
    : t("expires", { time: rel });
}

async function copy(text: string, message: string) {
  try {
    await navigator.clipboard.writeText(text);
    ElMessage.success(message);
  } catch {
    ElMessage.error("Copy failed");
  }
}

function copySubLink(user: User) {
  copy(absoluteSubscriptionUrl(user.subscription_url), t("usersTable.copied"));
}

function copyConfigs(user: User) {
  copy(user.links.join("\r\n"), t("usersTable.copied"));
}

const currentPage = computed({
  get: () => props.page,
  set: (v: number) => emit("update:page", v),
});
const pageSize = computed({
  get: () => props.limit,
  set: (v: number) => emit("update:limit", v),
});
</script>

<template>
  <div>
    <el-table
      :data="users"
      v-loading="loading"
      row-key="username"
      style="width: 100%"
      @row-click="(row: unknown) => emit('edit', asUser(row))"
    >
      <el-table-column :label="t('username')" min-width="180">
        <template #default="{ row }">
          <div class="username-cell">
            <span
              class="online-dot"
              :class="{ online: row.online_at }"
            />
            <span class="username-text">{{ row.username }}</span>
          </div>
        </template>
      </el-table-column>

      <el-table-column :label="t('usersTable.status')" min-width="160">
        <template #default="{ row }">
          <div class="status-cell">
            <el-tag :type="statusTagType(row.status)" size="small" round>
              {{ t(`status.${row.status}`) }}
            </el-tag>
            <span v-if="expiryText(asUser(row))" class="expiry">
              {{ expiryText(asUser(row)) }}
            </span>
          </div>
        </template>
      </el-table-column>

      <el-table-column :label="t('usersTable.dataUsage')" min-width="240">
        <template #default="{ row }">
          <div class="usage-cell">
            <el-progress
              :percentage="isUnlimited(row.data_limit) ? 100 : usagePercentage(row.used_traffic, row.data_limit)"
              :status="!isUnlimited(row.data_limit) && usagePercentage(row.used_traffic, row.data_limit) >= 100 ? 'exception' : undefined"
              :show-text="false"
              :stroke-width="6"
            />
            <div class="usage-text">
              <span>
                {{ formatBytes(row.used_traffic) }} /
                {{ usageTotalText(row.data_limit, row.data_limit_reset_strategy, t) }}
              </span>
              <span class="usage-total">
                {{ t("usersTable.total") }}: {{ formatBytes(row.lifetime_used_traffic) }}
              </span>
            </div>
          </div>
        </template>
      </el-table-column>

      <el-table-column
        :label="''"
        width="180"
        align="right"
      >
        <template #default="{ row }">
          <div class="actions" @click.stop>
            <el-tooltip :content="t('usersTable.copyLink')" placement="top">
              <el-button circle text :icon="LinkIcon" @click="copySubLink(asUser(row))" />
            </el-tooltip>
            <el-tooltip :content="t('usersTable.copyConfigs')" placement="top">
              <el-button circle text :icon="CopyDocument" @click="copyConfigs(asUser(row))" />
            </el-tooltip>
            <el-tooltip content="QR Code" placement="top">
              <el-button circle text :icon="Pointer" @click="emit('qr', asUser(row))" />
            </el-tooltip>
            <el-tooltip :content="t('userDialog.editUser')" placement="top">
              <el-button circle text :icon="Edit" @click="emit('edit', asUser(row))" />
            </el-tooltip>
            <el-tooltip :content="t('delete')" placement="top">
              <el-button
                circle
                text
                type="danger"
                :icon="Delete"
                @click="emit('remove', asUser(row))"
              />
            </el-tooltip>
          </div>
        </template>
      </el-table-column>

      <template #empty>
        <el-empty :description="t('usersTable.noUser')" />
      </template>
    </el-table>

    <div class="pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 30, 50, 100]"
        layout="total, sizes, prev, pager, next"
        background
      />
    </div>
  </div>
</template>

<style scoped>
.username-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}
.online-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--el-color-info);
  flex: 0 0 auto;
}
.online-dot.online {
  background: var(--el-color-success);
}
.status-cell {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.expiry {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}
.usage-cell {
  min-width: 200px;
}
.usage-text {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-top: 2px;
}
.actions {
  display: flex;
  justify-content: flex-end;
  gap: 2px;
}
.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
