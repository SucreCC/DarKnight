<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { usePageSeo } from '@/composables/usePageSeo'
import { usePlanCatalog } from '@/views/portal/Buy/usePlanCatalog'
import { currencySymbol, formatPrice } from '@/views/portal/Buy/plans'

const { t } = useI18n()
const router = useRouter()

usePageSeo({
  titleKey: 'site.pricing.seoTitle',
  descriptionKey: 'site.pricing.seoDescription',
  withHreflang: true
})

const { plans, currency, isLoading, isError } = usePlanCatalog()

function durationLabel(days: number): string {
  if (days <= 31) return t('site.pricing.perMonth')
  if (days <= 100) return t('site.pricing.perQuarter')
  if (days <= 190) return t('site.pricing.perHalfYear')
  return t('site.pricing.perYear')
}
</script>

<template>
  <section class="flex flex-col gap-8">
    <header class="text-center">
      <h1 class="m-0 text-3xl font-bold text-foreground">{{ t('site.pricing.title') }}</h1>
      <p class="mx-auto mt-3 max-w-2xl text-sm leading-relaxed text-muted-foreground">
        {{ t('site.pricing.subtitle') }}
      </p>
    </header>

    <div v-if="isLoading" class="grid gap-5 md:grid-cols-3">
      <Skeleton v-for="i in 3" :key="i" class="h-56 rounded-xl" />
    </div>

    <div
      v-else-if="isError"
      class="rounded-xl border border-border bg-card p-8 text-center text-sm text-muted-foreground"
    >
      {{ t('site.pricing.loadError') }}
    </div>

    <div v-else-if="plans.length === 0" class="rounded-xl border border-border bg-card p-8 text-center">
      <p class="m-0 text-sm text-muted-foreground">{{ t('site.pricing.empty') }}</p>
    </div>

    <div v-else class="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
      <article
        v-for="plan in plans"
        :key="plan.id"
        class="flex flex-col rounded-xl border border-border bg-card p-6"
      >
        <h2 class="m-0 text-lg font-semibold text-foreground">{{ plan.name }}</h2>
        <p class="mt-3 m-0">
          <span class="text-3xl font-bold text-foreground">
            {{ currencySymbol(currency) }}{{ formatPrice(plan.price) }}
          </span>
          <span class="ml-1 text-sm text-muted-foreground">{{ durationLabel(plan.durationDays) }}</span>
        </p>
        <ul class="mt-4 mb-6 flex flex-1 list-none flex-col gap-2 p-0">
          <li
            v-for="(feature, idx) in plan.features"
            :key="idx"
            class="text-sm leading-relaxed text-muted-foreground"
          >
            · {{ feature }}
          </li>
        </ul>
        <Button class="h-10 w-full" @click="router.push({ name: 'portal-register' })">
          {{ t('site.pricing.cta') }}
        </Button>
      </article>
    </div>

    <p class="m-0 text-center text-sm text-muted-foreground">
      {{ t('site.pricing.note') }}
      <router-link :to="{ name: 'login' }" class="text-primary hover:underline">
        {{ t('portal.login') }}
      </router-link>
    </p>
  </section>
</template>
