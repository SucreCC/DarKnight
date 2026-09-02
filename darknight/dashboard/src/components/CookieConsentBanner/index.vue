<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'

const COOKIE_CONSENT_KEY = 'darknight-cookie-consent'

const { t } = useI18n()
const visible = ref(false)

onMounted(() => {
  try {
    if (!localStorage.getItem(COOKIE_CONSENT_KEY)) {
      visible.value = true
    }
  } catch {
    visible.value = true
  }
})

function saveChoice(value: 'accepted' | 'declined') {
  try {
    localStorage.setItem(COOKIE_CONSENT_KEY, value)
  } catch {
    // ignore storage failures
  }
  visible.value = false
}

function accept() {
  saveChoice('accepted')
}

function decline() {
  saveChoice('declined')
}
</script>

<template>
  <div
    v-if="visible"
    class="fixed inset-x-0 bottom-0 z-50 border-t border-border bg-card/95 p-4 shadow-[0_-8px_30px_rgba(0,0,0,0.08)] backdrop-blur-sm"
    role="dialog"
    aria-live="polite"
    :aria-label="t('site.cookie.title')"
  >
    <div
      class="mx-auto flex max-w-5xl flex-col gap-3 sm:flex-row sm:items-center sm:justify-between sm:gap-6"
    >
      <div class="min-w-0 flex-1">
        <p class="m-0 text-sm font-medium text-foreground">{{ t('site.cookie.title') }}</p>
        <p class="mb-0 mt-1 text-sm leading-relaxed text-muted-foreground">
          {{ t('site.cookie.message') }}
          <router-link
            :to="{ name: 'site-privacy' }"
            class="font-medium text-primary underline-offset-2 hover:underline"
          >
            {{ t('site.legal.privacy') }}
          </router-link>
        </p>
      </div>
      <div class="flex shrink-0 items-center gap-2">
        <Button variant="outline" class="h-10 px-5" @click="decline">
          {{ t('site.cookie.decline') }}
        </Button>
        <Button class="h-10 px-5" @click="accept">
          {{ t('site.cookie.accept') }}
        </Button>
      </div>
    </div>
  </div>
</template>
