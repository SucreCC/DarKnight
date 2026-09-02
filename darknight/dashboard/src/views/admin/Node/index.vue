<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Plus } from 'lucide-vue-next'
import { toast } from 'vue-sonner'
import { useNodesStore } from '@/store/modules/node'
import { useNodesQuery, useNodeMutations } from '@/api/node'
import type { NodeType } from '@/api/node/types'
import { useConfirm } from '@/composables/useConfirm'
import { Button } from '@/components/ui/button'
import NodesTable from './components/NodesTable.vue'
import NodeDialog from './components/NodeDialog.vue'

const { t } = useI18n()
const { confirm } = useConfirm()
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
  try {
    await confirm({
      title: t('deleteNode.title'),
      description: t('deleteNode.prompt', { name: node.name }).replace(/<\/?b>/gi, ''),
      destructive: true
    })
  } catch {
    return
  }
  if (node.id == null) return
  await deleteNode.mutateAsync(node.id)
  toast.success(t('deleteNode.deleteSuccess', { name: node.name }))
}

async function onReconnect(node: NodeType) {
  if (node.id == null) return
  await reconnectNode.mutateAsync(node.id)
  toast.success(t('nodes.reconnecting'))
}
</script>

<template>
  <div class="flex max-w-6xl flex-col gap-4">
    <div>
      <h1 class="text-lg font-semibold text-foreground">{{ t('nodes.pageTitle') }}</h1>
      <p class="mt-1 text-sm text-muted-foreground">{{ t('nodes.pageDesc') }}</p>
    </div>

    <div class="flex items-center gap-3">
      <div class="flex-1" />
      <Button @click="store.openCreate()">
        <Plus class="size-4" />
        {{ t('nodes.addNode') }}
      </Button>
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
