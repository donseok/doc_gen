<script setup>
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useDocumentStore } from '@/stores/document'
import { documentsApi } from '@/api/documents'

const { t } = useI18n()
const documentStore = useDocumentStore()

const loading = ref(false)
const filter = ref('all')

const filteredDocuments = computed(() => {
  if (filter.value === 'all') {
    return documentStore.documents
  }
  return documentStore.documents.filter(doc => doc.status === filter.value)
})

onMounted(async () => {
  loading.value = true
  await documentStore.fetchDocuments()
  loading.value = false
})

const getStatusClass = (status) => {
  const classes = {
    'completed': 'status-success',
    'processing': 'status-processing',
    'failed': 'status-error',
    'pending': 'status-pending'
  }
  return classes[status] || 'status-pending'
}

const getStatusText = (status) => {
  const texts = {
    'completed': t('documents.statusCompleted'),
    'processing': t('documents.statusProcessing'),
    'failed': t('documents.statusFailed'),
    'pending': t('documents.statusPending')
  }
  return texts[status] || status
}

const handleDownload = async (doc) => {
  try {
    await documentsApi.download(doc.id)
  } catch (error) {
    console.error('Download failed:', error)
  }
}

const handleDelete = async (doc) => {
  if (confirm(t('documents.confirmDelete'))) {
    await documentStore.deleteDocument(doc.id)
  }
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString()
}
</script>

<template>
  <div class="documents-page">
    <header class="page-header">
      <h1>{{ t('documents.title') }}</h1>
      <p class="page-description">{{ t('documents.description') }}</p>
    </header>

    <!-- Filter -->
    <div class="filter-bar">
      <button 
        :class="['filter-btn', { active: filter === 'all' }]"
        @click="filter = 'all'"
      >
        {{ t('documents.filterAll') }}
      </button>
      <button 
        :class="['filter-btn', { active: filter === 'completed' }]"
        @click="filter = 'completed'"
      >
        {{ t('documents.filterCompleted') }}
      </button>
      <button 
        :class="['filter-btn', { active: filter === 'processing' }]"
        @click="filter = 'processing'"
      >
        {{ t('documents.filterProcessing') }}
      </button>
      <button 
        :class="['filter-btn', { active: filter === 'failed' }]"
        @click="filter = 'failed'"
      >
        {{ t('documents.filterFailed') }}
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>{{ t('common.loading') }}</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="filteredDocuments.length === 0" class="empty-state">
      <div class="empty-icon">📋</div>
      <h3>{{ t('documents.empty') }}</h3>
      <p>{{ t('documents.emptyDescription') }}</p>
      <router-link to="/generate" class="btn btn-primary">
        {{ t('documents.startGenerate') }}
      </router-link>
    </div>

    <!-- Documents List -->
    <div v-else class="documents-list">
      <div 
        v-for="doc in filteredDocuments" 
        :key="doc.id" 
        class="document-card card"
      >
        <div class="doc-info">
          <h3 class="doc-title">{{ doc.title }}</h3>
          <p class="doc-filename">{{ doc.original_filename }}</p>
          <p class="doc-date">{{ formatDate(doc.created_at) }}</p>
        </div>
        <div class="doc-status">
          <span :class="['status-badge', getStatusClass(doc.status)]">
            {{ getStatusText(doc.status) }}
          </span>
        </div>
        <div class="doc-actions">
          <button 
            v-if="doc.status === 'completed'"
            class="btn btn-primary"
            @click="handleDownload(doc)"
          >
            {{ t('documents.download') }}
          </button>
          <button 
            class="btn btn-danger"
            @click="handleDelete(doc)"
          >
            {{ t('documents.delete') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.documents-page {
  padding: var(--spacing-lg) 0;
}

.page-header {
  text-align: center;
  margin-bottom: var(--spacing-xl);
}

.page-header h1 {
  font-size: 2.5rem;
  margin-bottom: var(--spacing-sm);
}

.page-description {
  color: var(--color-text-secondary);
  font-size: 1.125rem;
}

.filter-bar {
  display: flex;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-xl);
  justify-content: center;
  flex-wrap: wrap;
}

.filter-btn {
  padding: var(--spacing-sm) var(--spacing-lg);
  background: var(--color-surface);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.filter-btn:hover {
  background: var(--color-surface-hover);
}

.filter-btn.active {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: white;
}

.documents-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.document-card {
  display: grid;
  grid-template-columns: 1fr auto auto;
  gap: var(--spacing-lg);
  align-items: center;
}

.doc-title {
  font-size: 1.125rem;
  margin-bottom: var(--spacing-xs);
}

.doc-filename {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-xs);
}

.doc-date {
  font-size: 0.75rem;
  color: var(--color-text-muted);
}

.status-badge {
  padding: var(--spacing-xs) var(--spacing-md);
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  font-weight: 500;
}

.status-success {
  background: rgba(16, 185, 129, 0.2);
  color: var(--color-secondary);
}

.status-processing {
  background: rgba(245, 158, 11, 0.2);
  color: var(--color-accent);
}

.status-error {
  background: rgba(239, 68, 68, 0.2);
  color: var(--color-danger);
}

.status-pending {
  background: rgba(148, 163, 184, 0.2);
  color: var(--color-text-secondary);
}

.doc-actions {
  display: flex;
  gap: var(--spacing-sm);
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
  margin-bottom: var(--spacing-lg);
}

@media (max-width: 768px) {
  .document-card {
    grid-template-columns: 1fr;
    text-align: center;
  }
  
  .doc-actions {
    justify-content: center;
  }
}
</style>
