<script setup lang="ts">
import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

onMounted(() => {
  router.replace({
    name: 'portal-tickets',
    query: { ticketId: String(route.params.ticketId || '') }
  })
})
</script>

<template>
  <div />
</template>
