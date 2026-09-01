<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { Search } from 'lucide-vue-next'
import { Input } from '@/components/ui/input'
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
  router.push({ name: 'portal-docs-detail', params: { id } })
}
</script>

<template>
  <div
    class="max-w-3xl rounded-2xl border border-slate-200/80 bg-card p-6 shadow-sm dark:border-border md:p-8"
  >
    <div class="relative mb-8">
      <Search
        class="pointer-events-none absolute start-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground"
      />
      <Input
        v-model="keyword"
        class="h-11 rounded-xl ps-9"
        :placeholder="t('portal.docs.search')"
      />
    </div>

    <p v-if="!groups.length" class="py-10 text-center text-sm text-muted-foreground">
      {{ t('portal.docs.emptySearch') }}
    </p>

    <section v-for="group in groups" :key="group.id" class="mb-8 last:mb-0">
      <h2 class="mb-1 px-3 text-xl font-bold tracking-tight text-slate-900 dark:text-foreground">
        {{ t(group.titleKey) }}
      </h2>
      <div>
        <button
          v-for="article in group.articles"
          :key="article.id"
          type="button"
          class="flex w-full items-center justify-between gap-4 border-b border-slate-200 px-3 py-3.5 text-start transition-colors hover:bg-slate-50 dark:border-border dark:hover:bg-muted/50"
          @click="openArticle(article.id)"
        >
          <span class="text-sm font-normal leading-snug text-slate-700 dark:text-foreground/90">
            {{ t(article.titleKey) }}
          </span>
          <span class="shrink-0 text-xs tabular-nums text-slate-400 dark:text-muted-foreground">
            {{ article.updatedAt }}
          </span>
        </button>
      </div>
    </section>
  </div>
</template>
