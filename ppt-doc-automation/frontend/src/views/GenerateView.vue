<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter, useRoute } from 'vue-router'
import { generateApi } from '@/api/generate'
import { useDocumentStore } from '@/stores/document'
import { useTemplateStore } from '@/stores/template'

const { t } = useI18n()
const router = useRouter()
const route = useRoute()
const documentStore = useDocumentStore()
const templateStore = useTemplateStore()

const mdContent = ref('')
const selectedFile = ref(null)
const inputMode = ref('text') // 'text' or 'file'
const isGenerating = ref(false)
const error = ref(null)
const selectedTemplateId = ref(null)
const selectedTheme = ref('modern_blue')

const themes = [
  { id: 'modern_blue', name: '모던 블루', color: '#0070C0' },
  { id: 'corporate', name: '기업용', color: '#003366' },
  { id: 'dark', name: '다크 모드', color: '#00BCD4' },
  { id: 'minimal', name: '미니멀', color: '#333333' },
]

onMounted(async () => {
  // 템플릿 목록 로드
  await templateStore.fetchTemplates()

  // URL에서 템플릿 ID 확인
  if (route.query.template) {
    selectedTemplateId.value = parseInt(route.query.template)
  }
})

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
    // 스마트 모드 옵션 명시적 전달
    const options = {
      smart_mode: true,
      theme: selectedTheme.value
    }
    const result = await generateApi.fromText(mdContent.value, selectedTemplateId.value, options)
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

const selectTemplate = (templateId) => {
  if (selectedTemplateId.value === templateId) {
    selectedTemplateId.value = null // 선택 해제
  } else {
    selectedTemplateId.value = templateId
  }
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

      <!-- Template & Theme Selection -->
      <div class="style-options">
        <!-- Template Selection -->
        <div class="option-section">
          <h3 class="option-title">
            <span class="option-icon">📑</span>
            템플릿 선택 (선택사항)
          </h3>
          <p class="option-description">
            업로드한 템플릿의 스타일(색상, 폰트)을 적용합니다. 선택하지 않으면 테마가 적용됩니다.
          </p>
          <div class="template-list" v-if="templateStore.templates.length > 0">
            <div
              v-for="template in templateStore.templates"
              :key="template.id"
              :class="['template-option', { selected: selectedTemplateId === template.id }]"
              @click="selectTemplate(template.id)"
            >
              <span class="template-icon">📑</span>
              <span class="template-name">{{ template.name }}</span>
              <span v-if="template.is_default" class="default-tag">기본</span>
            </div>
          </div>
          <p v-else class="no-templates">
            업로드된 템플릿이 없습니다.
            <router-link to="/templates">템플릿 업로드하기</router-link>
          </p>
        </div>

        <!-- Theme Selection (when no template selected) -->
        <div class="option-section" v-if="!selectedTemplateId">
          <h3 class="option-title">
            <span class="option-icon">🎨</span>
            테마 선택
          </h3>
          <div class="theme-list">
            <div
              v-for="theme in themes"
              :key="theme.id"
              :class="['theme-option', { selected: selectedTheme === theme.id }]"
              @click="selectedTheme = theme.id"
            >
              <span class="theme-color" :style="{ backgroundColor: theme.color }"></span>
              <span class="theme-name">{{ theme.name }}</span>
            </div>
          </div>
        </div>
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

/* Style Options */
.style-options {
  margin-bottom: var(--spacing-lg);
  padding: var(--spacing-lg);
  background: var(--color-surface);
  border-radius: var(--radius-lg);
}

.option-section {
  margin-bottom: var(--spacing-lg);
}

.option-section:last-child {
  margin-bottom: 0;
}

.option-title {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-size: 1rem;
  margin-bottom: var(--spacing-sm);
}

.option-icon {
  font-size: 1.25rem;
}

.option-description {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-md);
}

.template-list {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-sm);
}

.template-option {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-md);
  background: white;
  border: 2px solid #e0e0e0;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s;
}

.template-option:hover {
  border-color: var(--color-primary);
}

.template-option.selected {
  border-color: var(--color-primary);
  background: rgba(0, 112, 192, 0.1);
}

.template-icon {
  font-size: 1.25rem;
}

.template-name {
  font-weight: 500;
}

.default-tag {
  font-size: 0.7rem;
  background: var(--color-primary);
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
}

.no-templates {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

.no-templates a {
  color: var(--color-primary);
  text-decoration: underline;
}

.theme-list {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-sm);
}

.theme-option {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-md);
  background: white;
  border: 2px solid #e0e0e0;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s;
}

.theme-option:hover {
  border-color: var(--color-primary);
}

.theme-option.selected {
  border-color: var(--color-primary);
  background: rgba(0, 112, 192, 0.1);
}

.theme-color {
  width: 20px;
  height: 20px;
  border-radius: 4px;
  border: 1px solid rgba(0, 0, 0, 0.1);
}

.theme-name {
  font-weight: 500;
}
</style>
