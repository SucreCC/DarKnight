<script setup lang="ts">
import { useI18n } from "vue-i18n";
import { SUPPORTED_LOCALES, setLocale, type LocaleCode } from "@/app/i18n";

const { locale } = useI18n();

function onChange(value: LocaleCode) {
  setLocale(value);
}
</script>

<template>
  <el-select
    :model-value="locale"
    style="width: 120px"
    @update:model-value="onChange"
  >
    <el-option
      v-for="item in SUPPORTED_LOCALES"
      :key="item.value"
      :label="item.label"
      :value="item.value"
    />
  </el-select>
</template>
