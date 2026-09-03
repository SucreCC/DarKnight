<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ArrowRight, Cable, FileText, Lock, ShieldCheck, Sparkles, Zap } from 'lucide-vue-next'
import type { Component } from 'vue'
import { Button } from '@/components/ui/button'
import { useSiteSeo } from '@/composables/useSiteSeo'

const { t } = useI18n()
const router = useRouter()

useSiteSeo()

const features: { icon: Component; title: string; desc: string }[] = [
  { icon: Lock, title: 'site.home.feature1Title', desc: 'site.home.feature1Desc' },
  { icon: Cable, title: 'site.home.feature2Title', desc: 'site.home.feature2Desc' },
  { icon: FileText, title: 'site.home.feature3Title', desc: 'site.home.feature3Desc' }
]

const steps: { icon: Component; title: string; desc: string }[] = [
  { icon: Sparkles, title: 'site.home.step1Title', desc: 'site.home.step1Desc' },
  { icon: Zap, title: 'site.home.step2Title', desc: 'site.home.step2Desc' },
  { icon: ShieldCheck, title: 'site.home.step3Title', desc: 'site.home.step3Desc' }
]

const protocols = ['VLESS', 'VMess', 'Trojan', 'Shadowsocks'] as const

const faqItems = [1, 2, 3, 4, 5, 6, 7] as const

const quickLinks = [
  {
    name: 'site-pricing' as const,
    titleKey: 'site.menu.pricing',
    descKey: 'site.home.quickPricing'
  },
  {
    name: 'site-guides' as const,
    titleKey: 'site.menu.guides',
    descKey: 'site.home.quickGuides'
  },
  {
    name: 'site-faq' as const,
    titleKey: 'site.menu.faq',
    descKey: 'site.home.quickFaq'
  }
]
</script>

<template>
  <section class="flex flex-col gap-10 sm:gap-12">
    <!-- Hero -->
    <div
      class="home-hero relative overflow-hidden rounded-3xl bg-primary px-6 py-14 text-center text-primary-foreground sm:px-12 sm:py-16"
    >
      <div
        class="pointer-events-none absolute inset-0 opacity-30"
        aria-hidden="true"
        style="
          background:
            radial-gradient(ellipse 80% 60% at 20% 20%, rgba(255, 255, 255, 0.35), transparent 55%),
            radial-gradient(ellipse 70% 50% at 90% 80%, rgba(0, 0, 0, 0.18), transparent 50%);
        "
      />
      <div class="relative mx-auto max-w-2xl">
        <p
          class="home-fade m-0 text-sm font-medium tracking-wide text-primary-foreground/80"
        >
          DarKnight
        </p>
        <h1 class="home-fade home-fade-delay-1 m-0 mt-3 text-3xl font-bold leading-tight sm:text-5xl">
          {{ t('site.home.heroTitle') }}
        </h1>
        <p
          class="home-fade home-fade-delay-2 mx-auto mb-8 mt-5 max-w-xl text-base leading-relaxed text-primary-foreground/90 sm:text-lg"
        >
          {{ t('site.home.subtitle') }}
        </p>
        <div
          class="home-fade home-fade-delay-3 flex flex-col items-center justify-center gap-3 sm:flex-row"
        >
          <Button
            class="h-11 min-w-36 bg-primary-foreground text-primary hover:bg-primary-foreground/90"
            @click="router.push({ name: 'portal-register' })"
          >
            {{ t('site.home.getStarted') }}
          </Button>
          <Button
            variant="outline"
            class="h-11 min-w-36 border-primary-foreground/40 bg-transparent text-primary-foreground hover:bg-primary-foreground/10"
            @click="router.push({ name: 'site-pricing' })"
          >
            {{ t('site.menu.pricing') }}
          </Button>
        </div>
      </div>
    </div>

    <!-- How it works -->
    <section>
      <div class="mb-6 text-center">
        <h2 class="m-0 text-2xl font-bold text-foreground">{{ t('site.home.howTitle') }}</h2>
        <p class="mx-auto mt-2 max-w-xl text-sm leading-relaxed text-muted-foreground">
          {{ t('site.home.howSubtitle') }}
        </p>
      </div>
      <ol class="m-0 grid list-none gap-4 p-0 md:grid-cols-3">
        <li
          v-for="(step, index) in steps"
          :key="step.title"
          class="relative rounded-2xl border border-border bg-card p-6"
        >
          <div class="mb-4 flex items-center gap-3">
            <span
              class="inline-flex size-8 items-center justify-center rounded-full bg-primary/10 text-sm font-semibold text-primary"
            >
              {{ index + 1 }}
            </span>
            <component :is="step.icon" class="size-5 text-primary" aria-hidden="true" />
          </div>
          <h3 class="m-0 text-base font-semibold text-foreground">{{ t(step.title) }}</h3>
          <p class="mb-0 mt-2 text-sm leading-relaxed text-muted-foreground">
            {{ t(step.desc) }}
          </p>
        </li>
      </ol>
    </section>

    <!-- Features -->
    <section>
      <div class="mb-6 text-center">
        <h2 class="m-0 text-2xl font-bold text-foreground">{{ t('site.home.featuresTitle') }}</h2>
        <p class="mx-auto mt-2 max-w-xl text-sm leading-relaxed text-muted-foreground">
          {{ t('site.home.featuresSubtitle') }}
        </p>
      </div>
      <div class="grid gap-5 md:grid-cols-3">
        <article
          v-for="item in features"
          :key="item.title"
          class="rounded-2xl border border-border bg-card p-6 transition hover:border-primary/30"
        >
          <component :is="item.icon" class="mb-3 size-7 text-primary" aria-hidden="true" />
          <h3 class="mb-2 text-lg font-semibold text-foreground">{{ t(item.title) }}</h3>
          <p class="m-0 text-sm leading-relaxed text-muted-foreground">{{ t(item.desc) }}</p>
        </article>
      </div>
    </section>

    <!-- Protocols + About -->
    <section class="grid gap-5 lg:grid-cols-2">
      <div class="rounded-2xl border border-border bg-card p-6 sm:p-8">
        <h2 class="m-0 text-xl font-semibold text-foreground">{{ t('site.home.protocolsTitle') }}</h2>
        <p class="mt-3 mb-5 text-sm leading-relaxed text-muted-foreground">
          {{ t('site.home.protocolsDesc') }}
        </p>
        <ul class="m-0 flex list-none flex-wrap gap-2 p-0">
          <li
            v-for="protocol in protocols"
            :key="protocol"
            class="rounded-full border border-primary/20 bg-primary/5 px-3 py-1 text-sm font-medium text-primary"
          >
            {{ protocol }}
          </li>
        </ul>
      </div>
      <div class="rounded-2xl border border-border bg-card p-6 sm:p-8">
        <h2 class="m-0 text-xl font-semibold text-foreground">{{ t('site.home.aboutTitle') }}</h2>
        <p class="mt-3 mb-5 text-sm leading-relaxed text-muted-foreground">
          {{ t('site.home.aboutDesc') }}
        </p>
        <Button variant="outline" class="h-10" @click="router.push({ name: 'site-guides' })">
          {{ t('site.home.viewGuides') }}
          <ArrowRight class="ml-1.5 size-4" />
        </Button>
      </div>
    </section>

    <!-- Explore -->
    <section>
      <div class="mb-6 text-center">
        <h2 class="m-0 text-2xl font-bold text-foreground">{{ t('site.home.exploreTitle') }}</h2>
      </div>
      <div class="grid gap-4 sm:grid-cols-3">
        <button
          v-for="link in quickLinks"
          :key="link.name"
          type="button"
          class="group rounded-2xl border border-border bg-card p-5 text-left transition hover:border-primary/40 hover:bg-primary/5"
          @click="router.push({ name: link.name })"
        >
          <p class="m-0 flex items-center gap-2 text-base font-semibold text-foreground">
            {{ t(link.titleKey) }}
            <ArrowRight
              class="size-4 text-muted-foreground transition group-hover:translate-x-0.5 group-hover:text-primary"
            />
          </p>
          <p class="mb-0 mt-2 text-sm leading-relaxed text-muted-foreground">
            {{ t(link.descKey) }}
          </p>
        </button>
      </div>
    </section>

    <!-- FAQ -->
    <section class="rounded-2xl border border-border bg-card p-6 sm:p-8">
      <div class="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h2 class="m-0 text-xl font-semibold text-foreground">{{ t('site.home.faqTitle') }}</h2>
          <p class="mb-0 mt-1 text-sm text-muted-foreground">{{ t('site.home.faqLead') }}</p>
        </div>
        <Button variant="link" class="h-auto p-0" @click="router.push({ name: 'site-faq' })">
          {{ t('site.home.viewAllFaq') }}
        </Button>
      </div>
      <div class="mt-5 flex flex-col gap-3">
        <details
          v-for="item in faqItems"
          :key="item"
          class="group rounded-xl border border-border px-4 py-3 open:bg-muted/30"
        >
          <summary
            class="cursor-pointer list-none text-sm font-medium text-foreground marker:content-none [&::-webkit-details-marker]:hidden"
          >
            <span class="flex items-start justify-between gap-3">
              <span>{{ t(`site.home.faq${item}Q`) }}</span>
              <span class="text-muted-foreground transition group-open:rotate-45">+</span>
            </span>
          </summary>
          <p class="mb-0 mt-3 text-sm leading-relaxed text-muted-foreground">
            {{ t(`site.home.faq${item}A`) }}
          </p>
        </details>
      </div>
    </section>

    <!-- Bottom CTA -->
    <section
      class="rounded-3xl border border-primary/20 bg-primary/5 px-6 py-10 text-center sm:px-10"
    >
      <h2 class="m-0 text-2xl font-bold text-foreground">{{ t('site.home.ctaTitle') }}</h2>
      <p class="mx-auto mt-3 max-w-lg text-sm leading-relaxed text-muted-foreground">
        {{ t('site.home.ctaDesc') }}
      </p>
      <div class="mt-6 flex flex-col items-center justify-center gap-3 sm:flex-row">
        <Button class="h-11 min-w-36" @click="router.push({ name: 'portal-register' })">
          {{ t('site.home.getStarted') }}
        </Button>
        <Button
          variant="outline"
          class="h-11 min-w-36"
          @click="router.push({ name: 'login' })"
        >
          {{ t('site.home.login') }}
        </Button>
      </div>
    </section>
  </section>
</template>

<style scoped>
.home-fade {
  animation: home-fade-up 0.55s ease both;
}

.home-fade-delay-1 {
  animation-delay: 0.08s;
}

.home-fade-delay-2 {
  animation-delay: 0.16s;
}

.home-fade-delay-3 {
  animation-delay: 0.24s;
}

@keyframes home-fade-up {
  from {
    opacity: 0;
    transform: translateY(10px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (prefers-reduced-motion: reduce) {
  .home-fade,
  .home-fade-delay-1,
  .home-fade-delay-2,
  .home-fade-delay-3 {
    animation: none;
  }
}
</style>
