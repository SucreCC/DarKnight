<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { Search } from '@element-plus/icons-vue'
import { DOC_ARTICLES, DOC_CATEGORIES } from './articles'

const { t } = useI18n()
const router = useRouter()
const keyword = ref('')

const groups = computed(() => {
  const query = keyword.value.trim().toLowerCase()
  return DOC_CATEGORIES.map((category) => ({
    ...category,
    articles: DOC_ARTICLES.filter((article) => {
      if (article.category !== category.id) return false
      if (!query) return true
      return t(article.titleKey).toLowerCase().includes(query)
    })
  })).filter((group) => group.articles.length)
})

function openArticle(id: string) {
  router.push({ name: 'site-docs-detail', params: { id } })
}
</script>

<template>
  <el-card shadow="never" class="docs-page">
    <el-input v-model="keyword" :placeholder="t('portal.docs.search')" clearable size="large">
      <template #suffix>
        <el-icon><Search /></el-icon>
      </template>
    </el-input>

    <el-empty v-if="!groups.length" :description="t('portal.docs.emptySearch')" />

    <section v-for="group in groups" :key="group.id" class="docs-group">
      <h2 class="docs-group-title">{{ t(group.titleKey) }}</h2>
      <button
        v-for="article in group.articles"
        :key="article.id"
        type="button"
        class="docs-item"
        @click="openArticle(article.id)"
      >
        <span class="docs-item-title">{{ t(article.titleKey) }}</span>
        <span class="docs-item-date">{{ article.updatedAt }}</span>
      </button>
    </section>
  </el-card>
</template>

<style scoped>
.docs-page {
  min-height: 360px;
}

.docs-group {
  margin-top: 28px;
}

.docs-group-title {
  margin: 0 0 4px;
  font-size: 16px;
  font-weight: 700;
  color: #303133;
}

.docs-item {
  display: flex;
  width: 100%;
  padding: 14px 0;
  font-size: 14px;
  color: #303133;
  text-align: left;
  cursor: pointer;
  background: transparent;
  border: none;
  border-bottom: 1px solid #ebeef5;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.docs-item:hover .docs-item-title {
  color: #20a397;
}

.docs-item-title {
  line-height: 1.5;
}

.docs-item-date {
  flex-shrink: 0;
  font-size: 13px;
  color: #909399;
}
</style>
