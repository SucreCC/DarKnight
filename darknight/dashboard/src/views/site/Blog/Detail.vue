<script setup lang="ts">
import { computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getBlogPostBySlug } from './articles'
import BlogArticle from './BlogArticle.vue'

const route = useRoute()
const router = useRouter()

const post = computed(() => getBlogPostBySlug(String(route.params.slug || '')))

watch(
  post,
  (value) => {
    if (!value) router.replace({ name: 'site-blog' })
  },
  { immediate: true }
)
</script>

<template>
  <BlogArticle v-if="post" :key="post.slug" :post="post" />
</template>
