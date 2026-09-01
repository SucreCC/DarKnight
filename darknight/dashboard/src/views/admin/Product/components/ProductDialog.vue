<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { Loader2, Plus, Trash2 } from 'lucide-vue-next'
import { toast } from 'vue-sonner'
import { extractErrorDetail } from '@/config/axios'
import { useProductMutations } from '@/api/product'
import type { Product, ProductCategory, ProductCycleInput } from '@/api/product/types'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

const props = defineProps<{ modelValue: boolean; product: Product | null }>()
const emit = defineEmits<{ 'update:modelValue': [value: boolean] }>()

const { t } = useI18n()
const { addProduct, updateProduct, addCycle, updateCycle, deleteCycle } = useProductMutations()

const isEditing = computed(() => !!props.product)
const errorMsg = ref('')
const submitting = ref(false)

const form = reactive({
  slug: '',
  name_zh: '',
  name_en: '',
  category: 'period' as ProductCategory,
  features_zh: [''] as string[],
  features_en: [''] as string[],
  display_cycle_key: '',
  sort_order: 0,
  is_listed: false,
  cycles: [] as (ProductCycleInput & { id?: number })[]
})

function defaultCycle(): ProductCycleInput {
  return {
    cycle_key: '',
    label_zh: '',
    label_en: '',
    price: 1,
    data_limit_gb: 100,
    duration_days: 30,
    is_listed: false,
    sort_order: 0
  }
}

function resetForm(product: Product | null) {
  errorMsg.value = ''
  if (product) {
    form.slug = product.slug
    form.name_zh = product.name_zh
    form.name_en = product.name_en
    form.category = product.category
    form.features_zh = product.features_zh.length ? [...product.features_zh] : ['']
    form.features_en = product.features_en.length ? [...product.features_en] : ['']
    form.display_cycle_key = product.display_cycle_key
    form.sort_order = product.sort_order
    form.is_listed = product.is_listed
    form.cycles = product.cycles.map((c) => ({
      id: c.id,
      cycle_key: c.cycle_key,
      label_zh: c.label_zh,
      label_en: c.label_en,
      price: c.price,
      data_limit_gb: c.data_limit_gb,
      duration_days: c.duration_days,
      is_listed: c.is_listed,
      sort_order: c.sort_order
    }))
  } else {
    form.slug = ''
    form.name_zh = ''
    form.name_en = ''
    form.category = 'period'
    form.features_zh = ['']
    form.features_en = ['']
    form.display_cycle_key = ''
    form.sort_order = 0
    form.is_listed = false
    form.cycles = [defaultCycle()]
  }
}

watch(
  () => props.modelValue,
  (open) => {
    if (open) resetForm(props.product)
  }
)

function addFeature(locale: 'zh' | 'en') {
  if (locale === 'zh') form.features_zh.push('')
  else form.features_en.push('')
}

function removeFeature(locale: 'zh' | 'en', index: number) {
  const list = locale === 'zh' ? form.features_zh : form.features_en
  if (list.length <= 1) {
    list[0] = ''
    return
  }
  list.splice(index, 1)
}

function addCycleRow() {
  form.cycles.push(defaultCycle())
}

function removeCycleRow(index: number) {
  if (form.cycles.length <= 1) return
  form.cycles.splice(index, 1)
}

function cleanFeatures(values: string[]) {
  return values.map((v) => v.trim()).filter(Boolean)
}

async function saveCycles(productId: number, original: Product['cycles']) {
  const keptIds = new Set<number>()

  for (const [index, cycle] of form.cycles.entries()) {
    const payload: ProductCycleInput = {
      cycle_key: cycle.cycle_key,
      label_zh: cycle.label_zh,
      label_en: cycle.label_en,
      price: cycle.price,
      data_limit_gb: cycle.data_limit_gb,
      duration_days: cycle.duration_days,
      is_listed: cycle.is_listed,
      sort_order: index
    }

    if (cycle.id) {
      keptIds.add(cycle.id)
      await updateCycle.mutateAsync({
        productId,
        cycleId: cycle.id,
        body: payload
      })
    } else {
      await addCycle.mutateAsync({ productId, body: payload })
    }
  }

  for (const old of original) {
    if (!keptIds.has(old.id)) {
      await deleteCycle.mutateAsync({ productId, cycleId: old.id })
    }
  }
}

async function onSubmit() {
  errorMsg.value = ''
  submitting.value = true
  try {
    const cycles = form.cycles.map((c, i) => ({ ...c, sort_order: i }))
    const displayKey = form.display_cycle_key || cycles[0]?.cycle_key || ''

    if (isEditing.value && props.product) {
      await updateProduct.mutateAsync({
        id: props.product.id,
        body: {
          slug: form.slug,
          name_zh: form.name_zh,
          name_en: form.name_en,
          category: form.category,
          features_zh: cleanFeatures(form.features_zh),
          features_en: cleanFeatures(form.features_en),
          display_cycle_key: displayKey,
          sort_order: form.sort_order,
          is_listed: form.is_listed
        }
      })
      await saveCycles(props.product.id, props.product.cycles)
      toast.success(t('products.saveSuccess'))
    } else {
      await addProduct.mutateAsync({
        slug: form.slug,
        name_zh: form.name_zh,
        name_en: form.name_en,
        category: form.category,
        features_zh: cleanFeatures(form.features_zh),
        features_en: cleanFeatures(form.features_en),
        display_cycle_key: displayKey,
        sort_order: form.sort_order,
        is_listed: form.is_listed,
        cycles
      })
      toast.success(t('products.createSuccess'))
    }
    emit('update:modelValue', false)
  } catch (err: unknown) {
    const detail = extractErrorDetail(err)
    errorMsg.value =
      typeof detail === 'string' ? detail : detail ? JSON.stringify(detail) : String(err)
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <Dialog :open="modelValue" @update:open="(v: boolean) => emit('update:modelValue', v)">
    <DialogContent class="max-h-[90vh] overflow-y-auto sm:max-w-3xl">
      <DialogHeader>
        <DialogTitle>
          {{ isEditing ? t('products.editTitle') : t('products.createTitle') }}
        </DialogTitle>
      </DialogHeader>

      <form class="grid gap-4" @submit.prevent="onSubmit">
        <div class="grid gap-4 sm:grid-cols-2">
          <div class="space-y-2">
            <Label for="product-slug">{{ t('products.slug') }}</Label>
            <Input id="product-slug" v-model="form.slug" />
          </div>
          <div class="space-y-2">
            <Label for="product-sort">{{ t('products.sortOrder') }}</Label>
            <Input id="product-sort" v-model.number="form.sort_order" type="number" />
          </div>
          <div class="space-y-2">
            <Label for="product-name-zh">{{ t('products.nameZh') }}</Label>
            <Input id="product-name-zh" v-model="form.name_zh" />
          </div>
          <div class="space-y-2">
            <Label for="product-name-en">{{ t('products.nameEn') }}</Label>
            <Input id="product-name-en" v-model="form.name_en" />
          </div>
          <div class="space-y-2">
            <Label for="product-category">{{ t('products.category') }}</Label>
            <select
              id="product-category"
              v-model="form.category"
              class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 text-sm"
            >
              <option value="period">{{ t('portal.buy.filter.period') }}</option>
              <option value="traffic">{{ t('portal.buy.filter.traffic') }}</option>
            </select>
          </div>
          <div class="space-y-2">
            <Label for="product-display-cycle">{{ t('products.displayCycle') }}</Label>
            <Input id="product-display-cycle" v-model="form.display_cycle_key" />
          </div>
        </div>

        <label class="flex items-center gap-2 text-sm">
          <input v-model="form.is_listed" type="checkbox" class="size-4 rounded border" />
          {{ t('products.listed') }}
        </label>

        <div class="grid gap-4 sm:grid-cols-2">
          <div class="space-y-2">
            <div class="flex items-center justify-between">
              <Label>{{ t('products.featuresZh') }}</Label>
              <Button type="button" variant="ghost" size="sm" @click="addFeature('zh')">
                <Plus class="size-4" />
              </Button>
            </div>
            <div v-for="(_, i) in form.features_zh" :key="`zh-${i}`" class="flex gap-2">
              <Input v-model="form.features_zh[i]" />
              <Button type="button" variant="ghost" size="icon" @click="removeFeature('zh', i)">
                <Trash2 class="size-4" />
              </Button>
            </div>
          </div>
          <div class="space-y-2">
            <div class="flex items-center justify-between">
              <Label>{{ t('products.featuresEn') }}</Label>
              <Button type="button" variant="ghost" size="sm" @click="addFeature('en')">
                <Plus class="size-4" />
              </Button>
            </div>
            <div v-for="(_, i) in form.features_en" :key="`en-${i}`" class="flex gap-2">
              <Input v-model="form.features_en[i]" />
              <Button type="button" variant="ghost" size="icon" @click="removeFeature('en', i)">
                <Trash2 class="size-4" />
              </Button>
            </div>
          </div>
        </div>

        <div class="space-y-3">
          <div class="flex items-center justify-between">
            <Label>{{ t('products.cycles') }}</Label>
            <Button type="button" variant="outline" size="sm" @click="addCycleRow">
              <Plus class="size-4" />
              {{ t('products.addCycle') }}
            </Button>
          </div>
          <div
            v-for="(cycle, index) in form.cycles"
            :key="index"
            class="grid gap-2 rounded-lg border border-border p-3 sm:grid-cols-4"
          >
            <Input v-model="cycle.cycle_key" :placeholder="t('products.cycleKey')" />
            <Input v-model="cycle.label_zh" :placeholder="t('products.labelZh')" />
            <Input v-model="cycle.label_en" :placeholder="t('products.labelEn')" />
            <Input v-model.number="cycle.price" type="number" step="0.01" :placeholder="t('products.price')" />
            <Input v-model.number="cycle.data_limit_gb" type="number" :placeholder="t('products.dataLimitGb')" />
            <Input v-model.number="cycle.duration_days" type="number" :placeholder="t('products.durationDays')" />
            <label class="flex items-center gap-2 text-xs sm:col-span-2">
              <input v-model="cycle.is_listed" type="checkbox" class="size-4 rounded border" />
              {{ t('products.listed') }}
            </label>
            <Button
              v-if="form.cycles.length > 1"
              type="button"
              variant="ghost"
              size="sm"
              class="justify-self-end"
              @click="removeCycleRow(index)"
            >
              <Trash2 class="size-4" />
            </Button>
          </div>
        </div>

        <Alert v-if="errorMsg" variant="destructive">
          <AlertDescription>{{ errorMsg }}</AlertDescription>
        </Alert>

        <DialogFooter>
          <Button type="button" variant="outline" @click="emit('update:modelValue', false)">
            {{ t('cancel') }}
          </Button>
          <Button type="submit" :disabled="submitting">
            <Loader2 v-if="submitting" class="me-2 size-4 animate-spin" />
            {{ t('confirm') }}
          </Button>
        </DialogFooter>
      </form>
    </DialogContent>
  </Dialog>
</template>
