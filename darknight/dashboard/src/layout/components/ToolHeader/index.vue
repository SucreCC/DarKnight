<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ChevronDown, LogOut, PanelLeft, Settings, User } from 'lucide-vue-next'
import { http } from '@/config/axios'
import { removeToken } from '@/utils/auth'
import { useAppStore } from '@/store/modules/app'
import { useTagsViewStore } from '@/store/modules/tagsView'
import ThemeToggle from '@/components/ThemeToggle/index.vue'
import LanguageSwitch from '@/components/LanguageSwitch/index.vue'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger
} from '@/components/ui/dropdown-menu'
import Breadcrumb from '../Breadcrumb/index.vue'

const emit = defineEmits<{ 'open-setting': [] }>()

const { t } = useI18n()
const router = useRouter()
const appStore = useAppStore()
const tagsViewStore = useTagsViewStore()

const adminName = ref('')

onMounted(async () => {
  try {
    const admin = await http<{ username: string }>('/admin')
    adminName.value = admin.username
  } catch {
    /* 401 由 axios 拦截器处理 */
  }
})

function logout() {
  removeToken()
  tagsViewStore.reset()
  router.push({ name: 'login' })
}
</script>

<template>
  <div
    class="flex h-14 shrink-0 items-center gap-3 border-b border-border bg-card px-4"
  >
    <Button
      variant="ghost"
      size="icon"
      type="button"
      :title="t('layout.toggleSidebar')"
      :aria-label="t('layout.toggleSidebar')"
      @click="appStore.toggleCollapsed()"
    >
      <PanelLeft class="size-4" />
    </Button>
    <Breadcrumb v-if="appStore.showBreadcrumb" />
    <div class="flex-1" />
    <LanguageSwitch />
    <ThemeToggle />
    <Button
      variant="ghost"
      size="icon"
      type="button"
      :title="t('layout.settings')"
      :aria-label="t('layout.settings')"
      @click="emit('open-setting')"
    >
      <Settings class="size-4" />
    </Button>
    <DropdownMenu>
      <DropdownMenuTrigger as-child>
        <Button variant="ghost" class="gap-1.5 text-foreground">
          <User class="size-4" />
          <span class="max-w-32 truncate">{{ adminName || 'admin' }}</span>
          <ChevronDown class="size-4 opacity-60" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" class="min-w-40">
        <DropdownMenuItem class="gap-2" @click="logout">
          <LogOut class="size-4" />
          {{ t('header.logout') }}
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  </div>
</template>
