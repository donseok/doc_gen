<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { generateApi } from '@/api/generate'
import { useDocumentStore } from '@/stores/document'

const { t } = useI18n()
const router = useRouter()
const documentStore = useDocumentStore()

const mdContent = ref('')
const selectedFile = ref(null)
const inputMode = ref('text') // 'text' or 'file'
const isGenerating = ref(false)
const error = ref(null)

const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file && file.name.endsWith('.md')) {
    selectedFile.value = file
    error.value = null
    
    // 파일 내용 읽기
    const reader = new FileReader()
    reader.onload = (e) => {
      mdContent.value = e.target.result
    }
    reader.readAsText(file)
  } else {
    error.value = t('generate.invalidFile')
  }
}

const handleGenerate = async () => {
  if (!mdContent.value.trim()) {
    error.value = t('generate.emptyContent')
    return
  }

  isGenerating.value = true
  error.value = null

  try {
    const result = await generateApi.fromText(mdContent.value)
    documentStore.addDocument(result)
    router.push('/documents')
  } catch (err) {
    error.value = err.message || t('generate.error')
  } finally {
    isGenerating.value = false
  }
}

const clearContent = () => {
  mdContent.value = ''
  selectedFile.value = null
  error.value = null
}
</script>

<template>
  <div class="generate-page">
    <header class="page-header">
      <h1>{{ t('generate.title') }}</h1>
      <p class="page-description">{{ t('generate.description') }}</p>
    </header>

    <div class="generate-container card">
      <!-- Input Mode Toggle -->
      <div class="mode-toggle">
        <button 
          :class="['mode-btn', { active: inputMode === 'text' }]"
          @click="inputMode = 'text'"
        >
          <span class="mode-icon">✍️</span>
          {{ t('generate.textInput') }}
        </button>
        <button 
          :class="['mode-btn', { active: inputMode === 'file' }]"
          @click="inputMode = 'file'"
        >
          <span class="mode-icon">📂</span>
          {{ t('generate.fileInput') }}
        </button>
      </div>

      <!-- File Upload -->
      <div v-if="inputMode === 'file'" class="file-upload-area">
        <label class="file-drop-zone">
          <input 
            type="file" 
            accept=".md" 
            @change="handleFileSelect"
            hidden
          />
          <div v-if="!selectedFile" class="drop-content">
            <span class="drop-icon">📄</span>
            <p>{{ t('generate.dropFile') }}</p>
            <span class="drop-hint">{{ t('generate.dropHint') }}</span>
          </div>
          <div v-else class="selected-file">
            <span class="file-icon">✅</span>
            <span class="file-name">{{ selectedFile.name }}</span>
            <button class="remove-btn" @click.prevent="clearContent">×</button>
          </div>
        </label>
      </div>

      <!-- Text Editor -->
      <div class="editor-area">
        <div class="editor-header">
          <span class="editor-label">{{ t('generate.markdownContent') }}</span>
          <button class="btn btn-secondary btn-sm" @click="clearContent">
            {{ t('common.clear') }}
          </button>
        </div>
        <textarea
          v-model="mdContent"
          class="textarea markdown-editor"
          :placeholder="t('generate.placeholder')"
          rows="15"
        ></textarea>
      </div>

      <!-- Error Message -->
      <div v-if="error" class="error-message">
        <span class="error-icon">⚠️</span>
        {{ error }}
      </div>

      <!-- Actions -->
      <div class="actions">
        <button 
          class="btn btn-primary btn-lg"
          :disabled="isGenerating || !mdContent.trim()"
          @click="handleGenerate"
        >
          <span v-if="isGenerating" class="spinner-sm"></span>
          <span v-else>🚀</span>
          {{ isGenerating ? t('generate.generating') : t('generate.generateButton') }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.generate-page {
  max-width: 900px;
  margin: 0 auto;
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

.generate-container {
  padding: var(--spacing-xl);
}

.mode-toggle {
  display: flex;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-lg);
  background: var(--color-surface);
  padding: var(--spacing-xs);
  border-radius: var(--radius-lg);
}

.mode-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-md);
  background: transparent;
  border: none;
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.mode-btn.active {
  background: var(--color-primary);
  color: white;
}

.mode-btn:hover:not(.active) {
  background: var(--color-surface-hover);
}

.file-upload-area {
  margin-bottom: var(--spacing-lg);
}

.file-drop-zone {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 150px;
  border: 2px dashed var(--color-surface-hover);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: border-color var(--transition-fast);
}

.file-drop-zone:hover {
  border-color: var(--color-primary);
}

.drop-content {
  text-align: center;
}

.drop-icon {
  font-size: 3rem;
  display: block;
  margin-bottom: var(--spacing-sm);
}

.drop-hint {
  font-size: 0.875rem;
  color: var(--color-text-muted);
}

.selected-file {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.file-icon {
  font-size: 1.5rem;
}

.file-name {
  font-weight: 500;
}

.remove-btn {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: none;
  background: var(--color-danger);
  color: white;
  cursor: pointer;
  font-size: 1rem;
  line-height: 1;
}

.editor-area {
  margin-bottom: var(--spacing-lg);
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-sm);
}

.editor-label {
  font-weight: 500;
  color: var(--color-text-secondary);
}

.btn-sm {
  padding: var(--spacing-xs) var(--spacing-md);
  font-size: 0.75rem;
}

.markdown-editor {
  font-family: 'Consolas', 'Monaco', monospace;
  min-height: 300px;
}

.error-message {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-md);
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid var(--color-danger);
  border-radius: var(--radius-md);
  color: var(--color-danger);
  margin-bottom: var(--spacing-lg);
}

.actions {
  display: flex;
  justify-content: center;
}

.spinner-sm {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
