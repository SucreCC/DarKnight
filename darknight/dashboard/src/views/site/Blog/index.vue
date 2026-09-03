<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'
import { usePageSeo } from '@/composables/usePageSeo'
import { listBlogPosts } from './articles'

const { t } = useI18n()
const router = useRouter()

usePageSeo({
  titleKey: 'site.blog.seoTitle',
  descriptionKey: 'site.blog.seoDescription',
  withHreflang: true
})

const posts = listBlogPosts()
</script>

<template>
  <section class="flex flex-col gap-8">
    <header class="text-center">
      <h1 class="m-0 text-3xl font-bold text-foreground">{{ t('site.blog.title') }}</h1>
      <p class="mx-auto mt-3 max-w-2xl text-sm leading-relaxed text-muted-foreground">
        {{ t('site.blog.subtitle') }}
      </p>
    </header>

    <div class="flex flex-col gap-4">
      <article
        v-for="post in posts"
        :key="post.slug"
        class="rounded-xl border border-border bg-card p-5 sm:p-6"
      >
        <p class="m-0 text-xs text-muted-foreground">{{ post.updatedAt }}</p>
        <h2 class="m-0 mt-2 text-lg font-semibold text-foreground">
          {{ t(post.titleKey) }}
        </h2>
        <p class="mb-0 mt-2 text-sm leading-relaxed text-muted-foreground">
          {{ t(post.descriptionKey) }}
        </p>
        <Button
          variant="link"
          class="mt-3 h-auto px-0"
          @click="router.push({ name: 'site-blog-detail', params: { slug: post.slug } })"
        >
          {{ t('site.blog.readMore') }}
        </Button>
      </article>
    </div>
  </section>
</template>
