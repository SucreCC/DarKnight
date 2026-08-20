<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Connection, Document, Lock } from '@element-plus/icons-vue'

const { t } = useI18n()
const router = useRouter()

const features = [
  {
    icon: Lock,
    title: 'site.home.feature1Title',
    desc: 'site.home.feature1Desc'
  },
  {
    icon: Connection,
    title: 'site.home.feature2Title',
    desc: 'site.home.feature2Desc'
  },
  {
    icon: Document,
    title: 'site.home.feature3Title',
    desc: 'site.home.feature3Desc'
  }
]
</script>

<template>
  <section class="site-home">
    <div class="hero">
      <h1>{{ t('site.home.title') }}</h1>
      <p class="hero-desc">{{ t('site.home.subtitle') }}</p>
      <div class="hero-actions">
        <el-button type="primary" size="large" @click="router.push({ name: 'portal-register' })">
          {{ t('site.home.getStarted') }}
        </el-button>
        <el-button size="large" @click="router.push({ name: 'site-docs' })">
          {{ t('site.home.viewDocs') }}
        </el-button>
      </div>
    </div>

    <div class="feature-grid">
      <el-card v-for="item in features" :key="item.title" shadow="never" class="feature-card">
        <el-icon :size="28" class="feature-icon"><component :is="item.icon" /></el-icon>
        <h3>{{ t(item.title) }}</h3>
        <p>{{ t(item.desc) }}</p>
      </el-card>
    </div>
  </section>
</template>

<style scoped>
.site-home {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.hero {
  padding: 48px 40px;
  text-align: center;
  background: linear-gradient(135deg, #20a397 0%, #17867c 100%);
  border-radius: 16px;
  color: #fff;
}

.hero h1 {
  margin: 0 0 16px;
  font-size: 36px;
  font-weight: 700;
}

.hero-desc {
  max-width: 640px;
  margin: 0 auto 28px;
  font-size: 16px;
  line-height: 1.7;
  opacity: 0.92;
}

.hero-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 20px;
}

.feature-card {
  min-height: 180px;
}

.feature-icon {
  margin-bottom: 12px;
  color: #20a397;
}

.feature-card h3 {
  margin: 0 0 8px;
  font-size: 18px;
}

.feature-card p {
  margin: 0;
  font-size: 14px;
  line-height: 1.6;
  color: #606266;
}

@media (width <= 900px) {
  .feature-grid {
    grid-template-columns: 1fr;
  }

  .hero {
    padding: 32px 24px;
  }

  .hero h1 {
    font-size: 28px;
  }

  .hero-actions {
    flex-direction: column;
    align-items: center;
  }
}
</style>
