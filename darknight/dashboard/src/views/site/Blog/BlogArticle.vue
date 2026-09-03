<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'
import { usePageSeo } from '@/composables/usePageSeo'
import type { BlogPost } from './articles'

const props = defineProps<{ post: BlogPost }>()

const { t } = useI18n()
const router = useRouter()

usePageSeo({
  titleKey: props.post.titleKey,
  descriptionKey: props.post.descriptionKey,
  withHreflang: true,
  blogPosting: {
    datePublished: props.post.publishedAt,
    dateModified: props.post.updatedAt
  }
})
</script>

<template>
  <article class="flex flex-col gap-8">
    <header class="text-center">
      <p class="m-0 text-xs text-muted-foreground">{{ post.updatedAt }}</p>
      <h1 class="m-0 mt-2 text-3xl font-bold text-foreground">{{ t(post.titleKey) }}</h1>
      <p class="mx-auto mt-3 max-w-2xl text-sm leading-relaxed text-muted-foreground">
        {{ t(post.descriptionKey) }}
      </p>
    </header>

    <div class="rounded-xl border border-border bg-card p-6 sm:p-8">
      <div class="flex flex-col gap-4">
        <p
          v-for="key in post.bodyKeys"
          :key="key"
          class="m-0 text-sm leading-relaxed text-foreground"
        >
          {{ t(key) }}
        </p>
      </div>
    </div>

    <div class="flex justify-center">
      <Button variant="outline" @click="router.push({ name: 'site-blog' })">
        {{ t('site.blog.backToList') }}
      </Button>
    </div>
  </article>
</template>
