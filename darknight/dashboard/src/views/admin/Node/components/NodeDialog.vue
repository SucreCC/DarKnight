<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { Loader2 } from 'lucide-vue-next'
import { toast } from 'vue-sonner'
import { extractErrorDetail } from '@/config/axios'
import { useNodeMutations } from '@/api/node'
import { defaultNode, type NodeType } from '@/api/node/types'
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

const props = defineProps<{ modelValue: boolean; node: NodeType | null }>()
const emit = defineEmits<{ 'update:modelValue': [value: boolean] }>()

const { t } = useI18n()
const { addNode, updateNode } = useNodeMutations()

const isEditing = computed(() => !!props.node)
const errorMsg = ref('')
const fieldErrors = reactive<Record<string, string>>({})
const form = reactive<NodeType>(defaultNode())

watch(
  () => props.modelValue,
  (open) => {
    errorMsg.value = ''
    Object.keys(fieldErrors).forEach((key) => delete fieldErrors[key])
    if (!open) return
    if (props.node) Object.assign(form, defaultNode(), props.node)
    else Object.assign(form, defaultNode())
  }
)

const submitting = ref(false)

function validate(): boolean {
  Object.keys(fieldErrors).forEach((key) => delete fieldErrors[key])
  const required = ['name', 'address', 'port', 'api_port'] as const
  let ok = true
  for (const key of required) {
    const value = form[key]
    if (value === '' || value == null || (typeof value === 'number' && Number.isNaN(value))) {
      fieldErrors[key] = t('login.fieldRequired')
      ok = false
    }
  }
  return ok
}

function setNumber(field: 'port' | 'api_port' | 'usage_coefficient', value: string | number) {
  const n = typeof value === 'number' ? value : Number(value)
  form[field] = Number.isFinite(n) ? n : (field === 'usage_coefficient' ? 0 : 1)
}

async function onSubmit() {
  if (!validate()) return
  errorMsg.value = ''
  submitting.value = true
  try {
    if (isEditing.value) {
      await updateNode.mutateAsync({ ...form })
      toast.success(t('nodes.editNode'))
    } else {
      await addNode.mutateAsync({ ...form })
      toast.success(t('nodes.addNodeSuccess', { name: form.name }))
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
  <Dialog
    :open="modelValue"
    @update:open="(v: boolean) => emit('update:modelValue', v)"
  >
    <DialogContent class="sm:max-w-lg">
      <DialogHeader>
        <DialogTitle>
          {{ isEditing ? t('nodes.editNodeTitle') : t('nodes.createTitle') }}
        </DialogTitle>
      </DialogHeader>

      <form class="grid gap-4" @submit.prevent="onSubmit">
        <div class="space-y-2">
          <Label for="node-name">{{ t('nodes.nodeName') }}</Label>
          <Input
            id="node-name"
            v-model="form.name"
            :aria-invalid="!!fieldErrors.name"
          />
          <p v-if="fieldErrors.name" class="text-xs text-destructive">{{ fieldErrors.name }}</p>
        </div>

        <div class="space-y-2">
          <Label for="node-address">{{ t('nodes.nodeAddress') }}</Label>
          <Input
            id="node-address"
            v-model="form.address"
            :aria-invalid="!!fieldErrors.address"
          />
          <p v-if="fieldErrors.address" class="text-xs text-destructive">
            {{ fieldErrors.address }}
          </p>
        </div>

        <div class="grid gap-4 sm:grid-cols-2">
          <div class="space-y-2">
            <Label for="node-port">{{ t('nodes.nodePort') }}</Label>
            <Input
              id="node-port"
              type="number"
              min="1"
              :model-value="form.port"
              :aria-invalid="!!fieldErrors.port"
              @update:model-value="(v) => setNumber('port', v)"
            />
            <p v-if="fieldErrors.port" class="text-xs text-destructive">{{ fieldErrors.port }}</p>
          </div>
          <div class="space-y-2">
            <Label for="node-api-port">{{ t('nodes.nodeAPIPort') }}</Label>
            <Input
              id="node-api-port"
              type="number"
              min="1"
              :model-value="form.api_port"
              :aria-invalid="!!fieldErrors.api_port"
              @update:model-value="(v) => setNumber('api_port', v)"
            />
            <p v-if="fieldErrors.api_port" class="text-xs text-destructive">
              {{ fieldErrors.api_port }}
            </p>
          </div>
        </div>

        <div class="space-y-2">
          <Label for="node-usage">{{ t('nodes.usageCoefficient') }}</Label>
          <Input
            id="node-usage"
            type="number"
            min="0"
            step="0.1"
            :model-value="form.usage_coefficient"
            @update:model-value="(v) => setNumber('usage_coefficient', v)"
          />
        </div>

        <label
          v-if="!isEditing"
          class="flex items-start gap-2 text-sm text-foreground"
        >
          <input
            v-model="form.add_as_new_host"
            type="checkbox"
            class="mt-0.5 size-4 rounded border border-input accent-primary"
          />
          <span>{{ t('nodes.addHostForEveryInbound') }}</span>
        </label>

        <Alert v-if="errorMsg" variant="destructive">
          <AlertDescription>{{ errorMsg }}</AlertDescription>
        </Alert>
      </form>

      <DialogFooter>
        <Button variant="outline" type="button" @click="emit('update:modelValue', false)">
          {{ t('cancel') }}
        </Button>
        <Button type="button" :disabled="submitting" @click="onSubmit">
          <Loader2 v-if="submitting" class="size-4 animate-spin" />
          {{ isEditing ? t('nodes.editNode') : t('nodes.addNode') }}
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
