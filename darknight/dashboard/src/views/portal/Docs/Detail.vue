<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import { Download } from 'lucide-vue-next'
import { fetchPortalMe } from '@/api/portal'
import type { PortalUser } from '@/api/portal/types'
import { Button } from '@/components/ui/button'
import { getDocById } from './articles'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const user = ref<PortalUser | null>(null)

const article = computed(() => getDocById(String(route.params.id || '')))

onMounted(async () => {
  if (!article.value) {
    router.replace({ name: 'portal-docs' })
    return
  }
  try {
    user.value = await fetchPortalMe()
  } catch {
    /* 401 handled by axios */
  }
})

function requireSubscription(): string | null {
  const url = user.value?.subscription_url
  if (!url) {
    toast.warning(t('portal.docs.needSubscription'))
    return null
  }
  return url
}

async function copySubscription() {
  const url = requireSubscription()
  if (!url) return
  await navigator.clipboard.writeText(url)
  toast.success(t('portal.docs.copySuccess'))
}

function importClash() {
  const url = requireSubscription()
  if (!url) return
  window.location.href = `clash://install-config?url=${encodeURIComponent(url)}`
}

function importShadowrocket() {
  const url = requireSubscription()
  if (!url) return
  window.location.href = `shadowrocket://add/sub://${btoa(url)}`
}
</script>

<template>
  <div
    v-if="article"
    class="max-w-3xl rounded-xl border border-border bg-card p-6 leading-relaxed text-foreground"
  >
    <template v-for="(block, index) in article.blocks" :key="index">
      <p v-if="block.type === 'lead'" class="mb-7 text-base font-bold">
        {{ t(block.textKey) }}
      </p>

      <div v-else-if="block.type === 'step'" class="mb-3 mt-7">
        <h3 class="mb-2.5 text-base font-bold">{{ t(block.titleKey) }}</h3>
        <p v-if="block.bodyKey" class="mb-3 text-sm text-muted-foreground">
          {{ t(block.bodyKey) }}
        </p>
      </div>

      <p
        v-else-if="block.type === 'paragraph'"
        class="mb-3 text-sm text-muted-foreground"
      >
        {{ t(block.textKey) }}
      </p>

      <div v-else-if="block.type === 'downloads'" class="my-3 flex flex-col gap-3">
        <a
          v-for="item in block.items"
          :key="item.url"
          class="inline-flex h-11 w-full items-center justify-center gap-2 rounded-md bg-primary text-sm font-semibold text-primary-foreground transition-colors hover:bg-primary/90"
          :href="item.url"
          target="_blank"
          rel="noopener noreferrer"
        >
          <Download class="size-4" />
          {{ t(item.labelKey) }}
        </a>
      </div>

      <div
        v-else-if="block.type === 'note'"
        class="my-3 rounded-lg bg-muted p-4 text-[13px] text-muted-foreground"
      >
        {{ t(block.textKey) }}
      </div>

      <Button
        v-else-if="block.type === 'copySub'"
        class="mt-2 mb-1 w-full"
        @click="copySubscription"
      >
        {{ t('portal.docs.copySub') }}
      </Button>

      <Button
        v-else-if="block.type === 'importClash'"
        class="mt-2 mb-1 w-full"
        @click="importClash"
      >
        {{ t('portal.docs.importClash') }}
      </Button>

      <Button
        v-else-if="block.type === 'importShadowrocket'"
        class="mt-2 mb-1 w-full"
        @click="importShadowrocket"
      >
        {{ t('portal.docs.importShadowrocket') }}
      </Button>
    </template>
  </div>
</template>
