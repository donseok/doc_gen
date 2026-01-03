<script setup>
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'

const props = defineProps({
  template: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['delete'])

const { t } = useI18n()
const router = useRouter()

const useTemplate = () => {
  router.push({ path: '/generate', query: { template: props.template.id } })
}

const deleteTemplate = () => {
  emit('delete', props.template.id)
}
</script>

<template>
  <div class="template-card card">
    <div class="template-thumbnail">
      <img
        v-if="template.thumbnail_path"
        :src="template.thumbnail_path"
        :alt="template.name"
      />
      <div v-else class="thumbnail-placeholder">
        <span class="placeholder-icon">📑</span>
      </div>
      <div v-if="template.is_default" class="default-badge">
        {{ t('templates.default') }}
      </div>
      <button class="delete-btn" @click.stop="deleteTemplate" title="삭제">
        &times;
      </button>
    </div>
    <div class="template-info">
      <h3 class="template-name">{{ template.name }}</h3>
      <p class="template-description">{{ template.description || t('templates.noDescription') }}</p>
    </div>
    <div class="template-actions">
      <button class="btn btn-primary" @click="useTemplate">
        {{ t('templates.useTemplate') }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.template-card {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 0;
}

.template-thumbnail {
  position: relative;
  height: 180px;
  background: var(--color-surface);
  overflow: hidden;
}

.template-thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.thumbnail-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--color-surface) 0%, var(--color-surface-hover) 100%);
}

.placeholder-icon {
  font-size: 4rem;
  opacity: 0.5;
}

.default-badge {
  position: absolute;
  top: var(--spacing-sm);
  left: var(--spacing-sm);
  background: var(--color-primary);
  color: white;
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--radius-sm);
  font-size: 0.75rem;
  font-weight: 500;
}

.delete-btn {
  position: absolute;
  top: var(--spacing-sm);
  right: var(--spacing-sm);
  width: 28px;
  height: 28px;
  border: none;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.5);
  color: white;
  font-size: 1.25rem;
  line-height: 1;
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.2s, background-color 0.2s;
}

.template-card:hover .delete-btn {
  opacity: 1;
}

.delete-btn:hover {
  background: rgba(220, 53, 69, 0.9);
}

.template-info {
  padding: var(--spacing-lg);
  flex: 1;
}

.template-name {
  font-size: 1.125rem;
  margin-bottom: var(--spacing-sm);
}

.template-description {
  color: var(--color-text-secondary);
  font-size: 0.875rem;
  line-height: 1.5;
}

.template-actions {
  padding: 0 var(--spacing-lg) var(--spacing-lg);
}

.template-actions .btn {
  width: 100%;
}
</style>
