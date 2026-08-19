<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { useNodesStore } from '@/store/modules/node'
import { useNodesQuery, useNodeMutations } from '@/api/node'
import type { NodeType } from '@/api/node/types'
import NodesTable from './components/NodesTable.vue'
import NodeDialog from './components/NodeDialog.vue'

const { t } = useI18n()
const store = useNodesStore()
const pollInterval = ref<number | undefined>(5000)
const { data, isFetching } = useNodesQuery(pollInterval)
const { deleteNode, reconnectNode } = useNodeMutations()

const nodes = computed<NodeType[]>(() => data.value ?? [])

const dialogVisible = computed({
  get: () => store.isCreating || !!store.editingNode,
  set: (v: boolean) => {
    if (!v) store.close()
  }
})

async function onRemove(node: NodeType) {
  const ok = await ElMessageBox.confirm(
    t('deleteNode.prompt', { name: node.name }),
    t('deleteNode.title'),
    { type: 'warning', dangerouslyUseHTMLString: true }
  )
    .then(() => true)
    .catch(() => false)
  if (!ok || node.id == null) return
  await deleteNode.mutateAsync(node.id)
  ElMessage.success(t('deleteNode.deleteSuccess', { name: node.name }))
}

async function onReconnect(node: NodeType) {
  if (node.id == null) return
  await reconnectNode.mutateAsync(node.id)
  ElMessage.success(t('nodes.reconnecting'))
}
</script>

<template>
  <div class="dk-page">
    <div class="dk-toolbar">
      <div class="dk-spacer" />
      <el-button type="primary" :icon="Plus" @click="store.openCreate()">
        {{ t('nodes.addNode') }}
      </el-button>
    </div>

    <NodesTable
      :nodes="nodes"
      :loading="isFetching"
      @edit="store.openEdit"
      @remove="onRemove"
      @reconnect="onReconnect"
    />

    <NodeDialog v-model="dialogVisible" :node="store.editingNode" />
  </div>
</template>
