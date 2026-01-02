<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useTemplateStore } from '@/stores/template'
import TemplateCard from '@/components/TemplateCard.vue'

const { t } = useI18n()
const templateStore = useTemplateStore()

const loading = ref(false)

onMounted(async () => {
  loading.value = true
  await templateStore.fetchTemplates()
  loading.value = false
})
</script>

<template>
  <div class="templates-page">
    <header class="page-header">
      <h1>{{ t('templates.title') }}</h1>
      <p class="page-description">{{ t('templates.description') }}</p>
    </header>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>{{ t('common.loading') }}</p>
    </div>

    <div v-else-if="templateStore.templates.length === 0" class="empty-state">
      <div class="empty-icon">📁</div>
      <h3>{{ t('templates.empty') }}</h3>
      <p>{{ t('templates.emptyDescription') }}</p>
    </div>

    <div v-else class="templates-grid">
      <TemplateCard
        v-for="template in templateStore.templates"
        :key="template.id"
        :template="template"
      />
    </div>
  </div>
</template>

<style scoped>
.templates-page {
  padding: var(--spacing-lg) 0;
}

.page-header {
  text-align: center;
  margin-bottom: var(--spacing-2xl);
}

.page-header h1 {
  font-size: 2.5rem;
  margin-bottom: var(--spacing-sm);
}

.page-description {
  color: var(--color-text-secondary);
  font-size: 1.125rem;
}

.templates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: var(--spacing-lg);
}

.loading-state,
.empty-state {
  text-align: center;
  padding: var(--spacing-2xl);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--color-surface);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto var(--spacing-md);
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: var(--spacing-md);
}

.empty-state h3 {
  margin-bottom: var(--spacing-sm);
}

.empty-state p {
  color: var(--color-text-secondary);
}
</style>
