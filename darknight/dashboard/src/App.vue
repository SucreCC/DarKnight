<script setup lang="ts">
import { computed } from "vue";
import { ElConfigProvider } from "element-plus";
import { useThemeStore } from "@/shared/stores/theme";
import { useI18n } from "vue-i18n";

// Ensure theme store is initialized (applies dark class on load).
useThemeStore();
const { locale } = useI18n();
const rtl = computed(() => (locale.value === "fa" ? "rtl" : "ltr"));
</script>

<template>
  <el-config-provider :locale="undefined">
    <div :dir="rtl" class="dk-app">
      <router-view />
    </div>
  </el-config-provider>
</template>

<style scoped>
.dk-app {
  height: 100%;
}
</style>
