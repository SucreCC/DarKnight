<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import QrcodeVue from 'qrcode.vue'
import { toast } from 'vue-sonner'
import type { User } from '@/api/user/types'
import { absoluteSubscriptionUrl } from '../helpers'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'

const props = defineProps<{
  modelValue: boolean
  user: User | null
}>()
const emit = defineEmits<{ 'update:modelValue': [value: boolean] }>()

const { t } = useI18n()

const subUrl = computed(() =>
  props.user ? absoluteSubscriptionUrl(props.user.subscription_url) : ''
)
const links = computed(() => props.user?.links ?? [])

async function copySub() {
  await navigator.clipboard.writeText(subUrl.value)
  toast.success(t('usersTable.copied'))
}
</script>

<template>
  <Dialog
    :open="modelValue"
    @update:open="(v: boolean) => emit('update:modelValue', v)"
  >
    <DialogContent class="max-h-[90vh] overflow-y-auto sm:max-w-lg">
      <DialogHeader>
        <DialogTitle>{{ t('qrcodeDialog.sublink') }}</DialogTitle>
      </DialogHeader>

      <div class="flex flex-col items-center gap-3">
        <QrcodeVue v-if="subUrl" :value="subUrl" :size="220" level="M" />
        <Input
          :model-value="subUrl"
          readonly
          class="cursor-pointer"
          @click="copySub"
        />
        <template v-if="links.length">
          <div class="w-full border-t border-border pt-3 text-center text-sm text-muted-foreground">
            Configs
          </div>
          <div class="flex flex-wrap justify-center gap-3">
            <div v-for="(link, i) in links" :key="i">
              <QrcodeVue :value="link" :size="120" level="M" />
            </div>
          </div>
        </template>
      </div>
    </DialogContent>
  </Dialog>
</template>
