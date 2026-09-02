<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { Loader2, Plus, Trash2 } from 'lucide-vue-next'
import { toast } from 'vue-sonner'
import { extractErrorDetail } from '@/config/axios'
import { useProductMutations } from '@/api/product'
import type { Product } from '@/api/product/types'
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
const { addProduct, updateProduct } = useProductMutations()

const isEditing = computed(() => !!props.product)
const errorMsg = ref('')
const submitting = ref(false)

const form = reactive({
  slug: '',
  name_zh: '',
  name_en: '',
  features_zh: [''] as string[],
  features_en: [''] as string[],
  price: 4.99,
  duration_days: 30
})

function resetForm(product: Product | null) {
  errorMsg.value = ''
  if (product) {
    form.slug = product.slug
    form.name_zh = product.name_zh
    form.name_en = product.name_en
    form.features_zh = product.features_zh.length ? [...product.features_zh] : ['']
    form.features_en = product.features_en.length ? [...product.features_en] : ['']
    form.price = product.price
    form.duration_days = product.duration_days
  } else {
    form.slug = ''
    form.name_zh = ''
    form.name_en = ''
    form.features_zh = ['']
    form.features_en = ['']
    form.price = 4.99
    form.duration_days = 30
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

function cleanFeatures(values: string[]) {
  return values.map((v) => v.trim()).filter(Boolean)
}

async function onSubmit() {
  errorMsg.value = ''
  submitting.value = true
  try {
    const body = {
      slug: form.slug,
      name_zh: form.name_zh,
      name_en: form.name_en,
      features_zh: cleanFeatures(form.features_zh),
      features_en: cleanFeatures(form.features_en),
      price: form.price,
      duration_days: form.duration_days
    }

    if (isEditing.value && props.product) {
      await updateProduct.mutateAsync({ id: props.product.id, body })
      toast.success(t('products.saveSuccess'))
    } else {
      await addProduct.mutateAsync({ ...body, is_listed: false })
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
          <div class="space-y-2 sm:col-span-2">
            <Label for="product-slug">{{ t('products.slug') }}</Label>
            <Input id="product-slug" v-model="form.slug" />
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
            <Label for="product-price">{{ t('products.price') }}</Label>
            <Input id="product-price" v-model.number="form.price" type="number" step="0.01" />
          </div>
          <div class="space-y-2">
            <Label for="product-duration">{{ t('products.durationDays') }}</Label>
            <Input id="product-duration" v-model.number="form.duration_days" type="number" />
          </div>
        </div>

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
