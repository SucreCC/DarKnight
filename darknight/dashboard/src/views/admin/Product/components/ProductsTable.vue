<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { Pencil, Trash2 } from 'lucide-vue-next'
import type { Product } from '@/api/product/types'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'

defineProps<{ products: Product[]; loading: boolean }>()
const emit = defineEmits<{
  edit: [product: Product]
  remove: [product: Product]
  toggleListed: [product: Product]
}>()

const { t } = useI18n()
</script>

<template>
  <div class="overflow-x-auto rounded-xl border border-border bg-card">
    <div v-if="loading && !products.length" class="space-y-3 p-4">
      <Skeleton v-for="i in 5" :key="i" class="h-10 w-full" />
    </div>

    <div
      v-else-if="!products.length"
      class="flex flex-col items-center gap-3 px-4 py-10 text-center text-muted-foreground"
    >
      <p class="text-sm">{{ t('products.empty') }}</p>
    </div>

    <table v-else class="w-full min-w-[880px] text-sm">
      <thead class="border-b border-border text-muted-foreground">
        <tr>
          <th class="px-4 py-3 text-start font-medium">{{ t('products.sortOrder') }}</th>
          <th class="px-4 py-3 text-start font-medium">{{ t('products.slug') }}</th>
          <th class="px-4 py-3 text-start font-medium">{{ t('products.nameZh') }}</th>
          <th class="px-4 py-3 text-start font-medium">{{ t('products.category') }}</th>
          <th class="px-4 py-3 text-start font-medium">{{ t('products.cycles') }}</th>
          <th class="px-4 py-3 text-start font-medium">{{ t('products.listed') }}</th>
          <th class="px-4 py-3 text-end font-medium" />
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="row in products"
          :key="row.id"
          class="border-b border-border last:border-0"
        >
          <td class="px-4 py-3 text-foreground">{{ row.sort_order }}</td>
          <td class="px-4 py-3 font-mono text-foreground">{{ row.slug }}</td>
          <td class="px-4 py-3 text-foreground">{{ row.name_zh }}</td>
          <td class="px-4 py-3 text-muted-foreground">{{ row.category }}</td>
          <td class="px-4 py-3 text-foreground">{{ row.cycles.length }}</td>
          <td class="px-4 py-3">
            <button type="button" @click="emit('toggleListed', row)">
              <Badge :variant="row.is_listed ? 'default' : 'secondary'">
                {{ row.is_listed ? t('products.listedYes') : t('products.listedNo') }}
              </Badge>
            </button>
          </td>
          <td class="px-4 py-3 text-end">
            <div class="inline-flex items-center gap-1">
              <Button variant="ghost" size="icon" type="button" @click="emit('edit', row)">
                <Pencil class="size-4" />
              </Button>
              <Button variant="ghost" size="icon" type="button" @click="emit('remove', row)">
                <Trash2 class="size-4 text-destructive" />
              </Button>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
