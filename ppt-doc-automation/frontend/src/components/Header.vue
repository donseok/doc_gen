<script setup>
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import { useI18n } from 'vue-i18n'

const { t, locale } = useI18n()

const isMenuOpen = ref(false)

const languages = [
  { code: 'ko', name: '한국어', flag: '🇰🇷' },
  { code: 'en', name: 'English', flag: '🇺🇸' },
  { code: 'vi', name: 'Tiếng Việt', flag: '🇻🇳' },
]

const changeLocale = (code) => {
  locale.value = code
  localStorage.setItem('locale', code)
}
</script>

<template>
  <header class="header">
    <div class="header-container">
      <RouterLink to="/" class="logo">
        <span class="logo-icon">📊</span>
        <span class="logo-text">PPT Doc Automation</span>
      </RouterLink>

      <nav class="nav-menu" :class="{ open: isMenuOpen }">
        <RouterLink to="/" class="nav-link">{{ t('nav.home') }}</RouterLink>
        <RouterLink to="/generate" class="nav-link">{{ t('nav.generate') }}</RouterLink>
        <RouterLink to="/templates" class="nav-link">{{ t('nav.templates') }}</RouterLink>
        <RouterLink to="/documents" class="nav-link">{{ t('nav.documents') }}</RouterLink>
      </nav>

      <div class="header-actions">
        <div class="language-selector">
          <button 
            v-for="lang in languages" 
            :key="lang.code"
            :class="['lang-btn', { active: locale === lang.code }]"
            @click="changeLocale(lang.code)"
            :title="lang.name"
          >
            {{ lang.flag }}
          </button>
        </div>

        <button 
          class="menu-toggle"
          @click="isMenuOpen = !isMenuOpen"
        >
          <span></span>
          <span></span>
          <span></span>
        </button>
      </div>
    </div>
  </header>
</template>

<style scoped>
.header {
  background: rgba(15, 23, 42, 0.95);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: var(--spacing-md) var(--spacing-xl);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-text);
  text-decoration: none;
}

.logo-icon {
  font-size: 1.5rem;
}

.nav-menu {
  display: flex;
  gap: var(--spacing-lg);
}

.nav-link {
  color: var(--color-text-secondary);
  text-decoration: none;
  font-weight: 500;
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
}

.nav-link:hover,
.nav-link.router-link-active {
  color: var(--color-primary-light);
  background: rgba(99, 102, 241, 0.1);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
}

.language-selector {
  display: flex;
  gap: var(--spacing-xs);
}

.lang-btn {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-md);
  border: 1px solid transparent;
  background: var(--color-surface);
  cursor: pointer;
  font-size: 1rem;
  transition: all var(--transition-fast);
}

.lang-btn:hover {
  background: var(--color-surface-hover);
}

.lang-btn.active {
  border-color: var(--color-primary);
  background: rgba(99, 102, 241, 0.2);
}

.menu-toggle {
  display: none;
  flex-direction: column;
  gap: 4px;
  padding: var(--spacing-sm);
  background: none;
  border: none;
  cursor: pointer;
}

.menu-toggle span {
  width: 24px;
  height: 2px;
  background: var(--color-text);
  transition: all var(--transition-fast);
}

@media (max-width: 768px) {
  .nav-menu {
    position: fixed;
    top: 60px;
    left: 0;
    right: 0;
    background: var(--color-bg-secondary);
    flex-direction: column;
    padding: var(--spacing-lg);
    gap: var(--spacing-sm);
    transform: translateY(-100%);
    opacity: 0;
    visibility: hidden;
    transition: all var(--transition-normal);
  }

  .nav-menu.open {
    transform: translateY(0);
    opacity: 1;
    visibility: visible;
  }

  .menu-toggle {
    display: flex;
  }
}
</style>
