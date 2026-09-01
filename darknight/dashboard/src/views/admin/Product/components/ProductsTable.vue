<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { Pencil, Trash2 } from 'lucide-vue-next'
import type { Product } from '@/api/product/types'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { Switch } from '@/components/ui/switch'

defineProps<{ products: Product[]; loading: boolean }>()
const emit = defineEmits<{
  edit: [product: Product]
  remove: [product: Product]
  setListed: [product: Product, listed: boolean]
}>()

const { t } = useI18n()

function primaryCycle(product: Product) {
  return product.cycles[0]
}
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
          <th class="px-4 py-3 text-start font-medium">{{ t('products.slug') }}</th>
          <th class="px-4 py-3 text-start font-medium">{{ t('products.nameZh') }}</th>
          <th class="px-4 py-3 text-start font-medium">{{ t('products.price') }}</th>
          <th class="px-4 py-3 text-start font-medium">{{ t('products.durationDays') }}</th>
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
          <td class="px-4 py-3 font-mono text-foreground">{{ row.slug }}</td>
          <td class="px-4 py-3 text-foreground">{{ row.name_zh }}</td>
          <td class="px-4 py-3 text-foreground">
            {{ primaryCycle(row)?.price ?? '—' }}
          </td>
          <td class="px-4 py-3 text-foreground">
            {{ primaryCycle(row)?.duration_days ?? '—' }}
          </td>
          <td class="px-4 py-3">
            <Switch
              :model-value="row.is_listed"
              @update:model-value="(v: boolean) => emit('setListed', row, v)"
            />
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
