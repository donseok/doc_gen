<script setup>
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
</script>

<template>
  <div class="home">
    <section class="hero">
      <div class="hero-content">
        <h1 class="hero-title">
          <span class="gradient-text">{{ t('home.title') }}</span>
        </h1>
        <p class="hero-description">{{ t('home.description') }}</p>
        <div class="hero-actions">
          <router-link to="/generate" class="btn btn-primary btn-lg">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/>
              <polyline points="14,2 14,8 20,8"/>
              <line x1="12" y1="18" x2="12" y2="12"/>
              <line x1="9" y1="15" x2="15" y2="15"/>
            </svg>
            {{ t('home.startButton') }}
          </router-link>
          <router-link to="/templates" class="btn btn-secondary btn-lg">
            {{ t('home.viewTemplates') }}
          </router-link>
        </div>
      </div>
      <div class="hero-visual">
        <div class="floating-card card-1">
          <div class="card-icon">📊</div>
          <div class="card-text">프레젠테이션</div>
        </div>
        <div class="floating-card card-2">
          <div class="card-icon">📝</div>
          <div class="card-text">마크다운</div>
        </div>
        <div class="floating-card card-3">
          <div class="card-icon">⚡</div>
          <div class="card-text">자동 생성</div>
        </div>
      </div>
    </section>

    <section class="features">
      <h2 class="section-title">{{ t('home.featuresTitle') }}</h2>
      <div class="features-grid">
        <div class="feature-card card">
          <div class="feature-icon">📄</div>
          <h3>{{ t('home.feature1Title') }}</h3>
          <p>{{ t('home.feature1Desc') }}</p>
        </div>
        <div class="feature-card card">
          <div class="feature-icon">🎨</div>
          <h3>{{ t('home.feature2Title') }}</h3>
          <p>{{ t('home.feature2Desc') }}</p>
        </div>
        <div class="feature-card card">
          <div class="feature-icon">🌐</div>
          <h3>{{ t('home.feature3Title') }}</h3>
          <p>{{ t('home.feature3Desc') }}</p>
        </div>
        <div class="feature-card card">
          <div class="feature-icon">📥</div>
          <h3>{{ t('home.feature4Title') }}</h3>
          <p>{{ t('home.feature4Desc') }}</p>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.home {
  padding: var(--spacing-xl) 0;
}

.hero {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-2xl);
  align-items: center;
  margin-bottom: var(--spacing-2xl);
  min-height: 60vh;
}

.hero-title {
  font-size: 3.5rem;
  font-weight: 700;
  line-height: 1.1;
  margin-bottom: var(--spacing-lg);
}

.gradient-text {
  background: linear-gradient(135deg, var(--color-primary-light) 0%, var(--color-secondary) 50%, var(--color-accent) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-description {
  font-size: 1.25rem;
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-xl);
  max-width: 500px;
}

.hero-actions {
  display: flex;
  gap: var(--spacing-md);
}

.btn-lg {
  padding: var(--spacing-md) var(--spacing-xl);
  font-size: 1rem;
}

.hero-visual {
  position: relative;
  height: 400px;
}

.floating-card {
  position: absolute;
  background: var(--color-bg-secondary);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-xl);
  border: 1px solid rgba(255, 255, 255, 0.1);
  animation: float 6s ease-in-out infinite;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-sm);
}

.card-1 {
  top: 20%;
  left: 10%;
  animation-delay: 0s;
}

.card-2 {
  top: 40%;
  right: 15%;
  animation-delay: 2s;
}

.card-3 {
  bottom: 15%;
  left: 30%;
  animation-delay: 4s;
}

.card-icon {
  font-size: 2rem;
}

.card-text {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-20px); }
}

.section-title {
  text-align: center;
  font-size: 2rem;
  margin-bottom: var(--spacing-xl);
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: var(--spacing-lg);
}

.feature-card {
  text-align: center;
}

.feature-icon {
  font-size: 3rem;
  margin-bottom: var(--spacing-md);
}

.feature-card h3 {
  margin-bottom: var(--spacing-sm);
  font-size: 1.25rem;
}

.feature-card p {
  color: var(--color-text-secondary);
  font-size: 0.875rem;
}

@media (max-width: 768px) {
  .hero {
    grid-template-columns: 1fr;
    text-align: center;
  }
  
  .hero-title {
    font-size: 2.5rem;
  }
  
  .hero-description {
    margin: 0 auto var(--spacing-xl);
  }
  
  .hero-actions {
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .hero-visual {
    display: none;
  }
}
</style>
