<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Plus } from 'lucide-vue-next'
import { toast } from 'vue-sonner'
import { extractErrorDetail } from '@/config/axios'
import { useProductsQuery, useProductMutations } from '@/api/product'
import type { Product } from '@/api/product/types'
import { useConfirm } from '@/composables/useConfirm'
import { Button } from '@/components/ui/button'
import ProductsTable from './components/ProductsTable.vue'
import ProductDialog from './components/ProductDialog.vue'

const { t } = useI18n()
const { confirm } = useConfirm()
const { data, isFetching } = useProductsQuery()
const { updateProduct, deleteProduct } = useProductMutations()

const products = computed<Product[]>(() => data.value ?? [])
const dialogOpen = ref(false)
const editingProduct = ref<Product | null>(null)

function openCreate() {
  editingProduct.value = null
  dialogOpen.value = true
}

function openEdit(product: Product) {
  editingProduct.value = product
  dialogOpen.value = true
}

async function onToggleListed(product: Product) {
  try {
    await updateProduct.mutateAsync({
      id: product.id,
      body: { is_listed: !product.is_listed }
    })
    toast.success(t('products.saveSuccess'))
  } catch (err: unknown) {
    const detail = extractErrorDetail(err)
    toast.error(typeof detail === 'string' ? detail : t('portal.requestFailed'))
  }
}

async function onRemove(product: Product) {
  try {
    await confirm({
      title: t('products.deleteTitle'),
      description: t('products.deleteConfirm', { name: product.name_zh }),
      destructive: true
    })
  } catch {
    return
  }
  try {
    await deleteProduct.mutateAsync(product.id)
    toast.success(t('products.deleteSuccess'))
  } catch (err: unknown) {
    const detail = extractErrorDetail(err)
    toast.error(typeof detail === 'string' ? detail : t('products.pendingBlock'))
  }
}
</script>

<template>
  <div class="flex max-w-6xl flex-col gap-4">
    <div class="flex items-center gap-3">
      <div class="flex-1" />
      <Button @click="openCreate">
        <Plus class="size-4" />
        {{ t('products.create') }}
      </Button>
    </div>

    <ProductsTable
      :products="products"
      :loading="isFetching"
      @edit="openEdit"
      @remove="onRemove"
      @toggle-listed="onToggleListed"
    />

    <ProductDialog v-model="dialogOpen" :product="editingProduct" />
  </div>
</template>
