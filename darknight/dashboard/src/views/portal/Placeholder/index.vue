<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'

const { t } = useI18n()
const route = useRoute()
</script>

<template>
  <el-card shadow="never" class="portal-placeholder">
    <el-empty :description="t('portal.comingSoon')">
      <template #description>
        <p>{{ t(route.meta.title as string) }}</p>
        <p>{{ t('portal.comingSoon') }}</p>
      </template>
    </el-empty>
  </el-card>
</template>

<style scoped>
.portal-placeholder {
  min-height: 320px;
}
</style>
