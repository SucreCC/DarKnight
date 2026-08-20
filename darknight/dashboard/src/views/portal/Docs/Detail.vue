<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Download } from '@element-plus/icons-vue'
import { fetchPortalMe } from '@/api/portal'
import type { PortalUser } from '@/api/portal/types'
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
    ElMessage.warning(t('portal.docs.needSubscription'))
    return null
  }
  return url
}

async function copySubscription() {
  const url = requireSubscription()
  if (!url) return
  await navigator.clipboard.writeText(url)
  ElMessage.success(t('portal.docs.copySuccess'))
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
  <el-card v-if="article" shadow="never" class="doc-detail">
    <template v-for="(block, index) in article.blocks" :key="index">
      <p v-if="block.type === 'lead'" class="doc-lead">{{ t(block.textKey) }}</p>

      <div v-else-if="block.type === 'step'" class="doc-step">
        <h3 class="doc-step-title">{{ t(block.titleKey) }}</h3>
        <p v-if="block.bodyKey" class="doc-step-body">{{ t(block.bodyKey) }}</p>
      </div>

      <p v-else-if="block.type === 'paragraph'" class="doc-paragraph">{{ t(block.textKey) }}</p>

      <div v-else-if="block.type === 'downloads'" class="doc-downloads">
        <a
          v-for="item in block.items"
          :key="item.url"
          class="doc-download"
          :href="item.url"
          target="_blank"
          rel="noopener noreferrer"
        >
          <el-icon :size="18"><Download /></el-icon>
          {{ t(item.labelKey) }}
        </a>
      </div>

      <div v-else-if="block.type === 'note'" class="doc-note">{{ t(block.textKey) }}</div>

      <el-button
        v-else-if="block.type === 'copySub'"
        class="doc-action"
        type="primary"
        @click="copySubscription"
      >
        {{ t('portal.docs.copySub') }}
      </el-button>

      <el-button
        v-else-if="block.type === 'importClash'"
        class="doc-action"
        type="primary"
        @click="importClash"
      >
        {{ t('portal.docs.importClash') }}
      </el-button>

      <el-button
        v-else-if="block.type === 'importShadowrocket'"
        class="doc-action"
        type="primary"
        @click="importShadowrocket"
      >
        {{ t('portal.docs.importShadowrocket') }}
      </el-button>
    </template>
  </el-card>
</template>

<style scoped>
.doc-detail {
  max-width: 880px;
  line-height: 1.7;
  color: #303133;
}

.doc-lead {
  margin: 0 0 28px;
  font-size: 16px;
  font-weight: 700;
}

.doc-step {
  margin: 28px 0 12px;
}

.doc-step-title {
  margin: 0 0 10px;
  font-size: 16px;
  font-weight: 700;
}

.doc-step-body,
.doc-paragraph {
  margin: 0 0 12px;
  font-size: 14px;
  color: #606266;
}

.doc-downloads {
  display: flex;
  margin: 12px 0;
  flex-direction: column;
  gap: 12px;
}

.doc-download {
  display: flex;
  padding: 14px 16px;
  font-size: 14px;
  font-weight: 600;
  color: #fff;
  text-decoration: none;
  background: #20a397;
  border-radius: 6px;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.doc-download:hover {
  color: #fff;
  background: #1b8c82;
}

.doc-note {
  padding: 14px 16px;
  margin: 12px 0 8px;
  font-size: 13px;
  color: #606266;
  background: #f4f6f8;
  border-radius: 6px;
}

.doc-action {
  width: 100%;
  margin: 8px 0 4px;
  background: #20a397;
  border-color: #20a397;
}

.doc-action:hover,
.doc-action:focus {
  background: #1b8c82;
  border-color: #1b8c82;
}
</style>
