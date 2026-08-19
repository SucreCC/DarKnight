<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const route = useRoute()

const items = computed(() =>
  route.matched.filter((item) => item.meta?.title).map((item) => t(item.meta.title as string))
)
</script>

<template>
  <el-breadcrumb separator="/">
    <el-breadcrumb-item v-for="item in items" :key="item">{{ item }}</el-breadcrumb-item>
  </el-breadcrumb>
</template>
