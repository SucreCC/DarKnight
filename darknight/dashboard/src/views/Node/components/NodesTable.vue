<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { Connection, Delete, Edit } from '@element-plus/icons-vue'
import { NODE_STATUS_TAG, type NodeStatus, type NodeType } from '@/api/node/types'

defineProps<{ nodes: NodeType[]; loading: boolean }>()
const emit = defineEmits<{
  edit: [node: NodeType]
  remove: [node: NodeType]
  reconnect: [node: NodeType]
}>()

const { t } = useI18n()
const asNode = (row: unknown) => row as NodeType
const statusTag = (status?: NodeStatus | null) => (status ? NODE_STATUS_TAG[status] : 'info')
</script>

<template>
  <el-table :data="nodes" v-loading="loading" row-key="id" style="width: 100%">
    <el-table-column :label="t('nodes.nodeName')" prop="name" min-width="140" />
    <el-table-column :label="t('nodes.nodeAddress')" prop="address" min-width="160" />
    <el-table-column :label="t('nodes.nodePort')" prop="port" width="100" />
    <el-table-column :label="t('nodes.nodeAPIPort')" prop="api_port" width="100" />
    <el-table-column label="Xray" prop="xray_version" width="110">
      <template #default="{ row }">{{ row.xray_version || '-' }}</template>
    </el-table-column>
    <el-table-column :label="t('usersTable.status')" min-width="140">
      <template #default="{ row }">
        <el-tooltip v-if="row.message" :content="row.message" placement="top">
          <el-tag :type="statusTag(row.status)" size="small" round>
            {{ t(`nodeModal.status.${row.status || 'disabled'}`) }}
          </el-tag>
        </el-tooltip>
        <el-tag v-else :type="statusTag(row.status)" size="small" round>
          {{ t(`nodeModal.status.${row.status || 'disabled'}`) }}
        </el-tag>
      </template>
    </el-table-column>
    <el-table-column :label="''" width="150" align="right">
      <template #default="{ row }">
        <el-tooltip :content="t('nodes.reconnect')" placement="top">
          <el-button circle text :icon="Connection" @click="emit('reconnect', asNode(row))" />
        </el-tooltip>
        <el-button circle text :icon="Edit" @click="emit('edit', asNode(row))" />
        <el-button circle text type="danger" :icon="Delete" @click="emit('remove', asNode(row))" />
      </template>
    </el-table-column>
    <template #empty>
      <el-empty :description="t('nodes.title')" />
    </template>
  </el-table>
</template>
