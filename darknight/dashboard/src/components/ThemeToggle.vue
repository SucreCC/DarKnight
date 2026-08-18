<script setup lang="ts">
import { computed } from "vue";
import { Moon, Sunny } from "@element-plus/icons-vue";
import { useThemeStore } from "@/shared/stores/theme";

const theme = useThemeStore();
const isDark = computed(() => theme.mode === "dark");
</script>

<template>
  <el-button circle text @click="theme.toggle()">
    <el-icon :size="18">
      <Moon v-if="isDark" />
      <Sunny v-else />
    </el-icon>
  </el-button>
</template>
