import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { NodeType } from '@/api/node/types'

export const useNodesStore = defineStore('nodes', () => {
  const editingNode = ref<NodeType | null>(null)
  const isCreating = ref(false)

  function openCreate() {
    editingNode.value = null
    isCreating.value = true
  }
  function openEdit(node: NodeType) {
    isCreating.value = false
    editingNode.value = node
  }
  function close() {
    isCreating.value = false
    editingNode.value = null
  }

  return { editingNode, isCreating, openCreate, openEdit, close }
})
