<script setup>
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const currentYear = new Date().getFullYear()
</script>

<template>
  <footer class="footer">
    <div class="footer-container">
      <div class="footer-content">
        <div class="footer-brand">
          <span class="logo-icon">📊</span>
          <span>PPT Doc Automation</span>
        </div>
        <p class="footer-copyright">
          © {{ currentYear }} PPT Doc Automation. {{ t('footer.rights') }}
        </p>
      </div>
      <div class="footer-links">
        <a href="#" class="footer-link">{{ t('footer.privacy') }}</a>
        <a href="#" class="footer-link">{{ t('footer.terms') }}</a>
        <a href="#" class="footer-link">{{ t('footer.contact') }}</a>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.footer {
  background: var(--color-bg-secondary);
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  padding: var(--spacing-xl) 0;
  margin-top: auto;
}

.footer-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 var(--spacing-xl);
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--spacing-lg);
}

.footer-brand {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-weight: 600;
  margin-bottom: var(--spacing-sm);
}

.logo-icon {
  font-size: 1.25rem;
}

.footer-copyright {
  color: var(--color-text-muted);
  font-size: 0.875rem;
}

.footer-links {
  display: flex;
  gap: var(--spacing-lg);
}

.footer-link {
  color: var(--color-text-secondary);
  font-size: 0.875rem;
  text-decoration: none;
  transition: color var(--transition-fast);
}

.footer-link:hover {
  color: var(--color-primary-light);
}

@media (max-width: 768px) {
  .footer-container {
    flex-direction: column;
    text-align: center;
  }
}
</style>
