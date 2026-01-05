<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useTemplateStore } from '@/stores/template'
import TemplateCard from '@/components/TemplateCard.vue'

const { t } = useI18n()
const templateStore = useTemplateStore()

const loading = ref(false)
const showUploadModal = ref(false)
const uploadForm = ref({
  file: null,
  name: '',
  description: '',
  category: 'group', // 기본값: 그룹사
  isDefault: false,
})
const uploadError = ref('')
const uploadSuccess = ref('')
const activeFilter = ref(null) // null: 전체, 'group': 그룹사, 'customer': 고객사

onMounted(async () => {
  loading.value = true
  await templateStore.fetchTemplates()
  loading.value = false
})

function setFilter(category) {
  activeFilter.value = category
  loading.value = true
  templateStore.fetchTemplates(category).finally(() => {
    loading.value = false
  })
}

function openUploadModal() {
  uploadForm.value = {
    file: null,
    name: '',
    description: '',
    category: 'group',
    isDefault: false,
  }
  uploadError.value = ''
  uploadSuccess.value = ''
  showUploadModal.value = true
}

function closeUploadModal() {
  showUploadModal.value = false
}

function handleFileChange(event) {
  const file = event.target.files[0]
  if (file) {
    uploadForm.value.file = file
    // 파일명에서 기본 이름 추출
    if (!uploadForm.value.name) {
      uploadForm.value.name = file.name.replace('.pptx', '')
    }
  }
}

async function handleUpload() {
  if (!uploadForm.value.file) {
    uploadError.value = 'PPTX 파일을 선택해주세요'
    return
  }
  if (!uploadForm.value.name.trim()) {
    uploadError.value = '템플릿 이름을 입력해주세요'
    return
  }

  uploadError.value = ''
  try {
    const response = await templateStore.uploadTemplate(
      uploadForm.value.file,
      uploadForm.value.name,
      uploadForm.value.description,
      uploadForm.value.category,
      uploadForm.value.isDefault
    )
    uploadSuccess.value = '템플릿이 업로드되었습니다!'
    setTimeout(() => {
      closeUploadModal()
    }, 1500)
  } catch (err) {
    uploadError.value = err.response?.data?.detail || '업로드 실패'
  }
}

async function handleDeleteTemplate(templateId) {
  if (!confirm('정말 이 템플릿을 삭제하시겠습니까?')) {
    return
  }
  try {
    await templateStore.deleteTemplate(templateId)
  } catch (err) {
    alert('삭제 실패: ' + (err.response?.data?.detail || err.message))
  }
}
</script>

<template>
  <div class="templates-page">
    <header class="page-header">
      <div class="header-content">
        <div>
          <h1>{{ t('templates.title') }}</h1>
          <p class="page-description">{{ t('templates.description') }}</p>
        </div>
        <button class="upload-btn" @click="openUploadModal">
          <span class="upload-icon">+</span>
          템플릿 업로드
        </button>
      </div>

      <!-- 필터 탭 -->
      <div class="filter-tabs">
        <button
          class="filter-tab"
          :class="{ active: activeFilter === null }"
          @click="setFilter(null)"
        >
          전체
        </button>
        <button
          class="filter-tab"
          :class="{ active: activeFilter === 'group' }"
          @click="setFilter('group')"
        >
          <span class="category-badge group">그룹사</span>
        </button>
        <button
          class="filter-tab"
          :class="{ active: activeFilter === 'customer' }"
          @click="setFilter('customer')"
        >
          <span class="category-badge customer">고객사</span>
        </button>
      </div>
    </header>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>{{ t('common.loading') }}</p>
    </div>

    <div v-else-if="templateStore.templates.length === 0" class="empty-state">
      <div class="empty-icon">📁</div>
      <h3>{{ t('templates.empty') }}</h3>
      <p>{{ t('templates.emptyDescription') }}</p>
      <button class="upload-btn-large" @click="openUploadModal">
        <span class="upload-icon">+</span>
        첫 번째 템플릿 업로드하기
      </button>
    </div>

    <div v-else class="templates-grid">
      <TemplateCard
        v-for="template in templateStore.templates"
        :key="template.id"
        :template="template"
        @delete="handleDeleteTemplate"
      />
    </div>

    <!-- 업로드 모달 -->
    <div v-if="showUploadModal" class="modal-overlay" @click.self="closeUploadModal">
      <div class="modal">
        <div class="modal-header">
          <h2>템플릿 업로드</h2>
          <button class="close-btn" @click="closeUploadModal">&times;</button>
        </div>

        <div class="modal-body">
          <p class="modal-description">
            PPTX 파일을 업로드하면 디자인 요소(색상, 폰트, 레이아웃)를 자동으로 분석합니다.
            업로드한 템플릿의 스타일로 새 PPT를 생성할 수 있습니다.
          </p>

          <div class="form-group">
            <label>PPTX 파일 *</label>
            <div class="file-input-wrapper">
              <input
                type="file"
                accept=".pptx"
                @change="handleFileChange"
                id="file-input"
              />
              <label for="file-input" class="file-input-label">
                {{ uploadForm.file ? uploadForm.file.name : '파일 선택...' }}
              </label>
            </div>
          </div>

          <div class="form-group">
            <label>템플릿 이름 *</label>
            <input
              type="text"
              v-model="uploadForm.name"
              placeholder="예: 기업 프레젠테이션 템플릿"
            />
          </div>

          <div class="form-group">
            <label>카테고리 *</label>
            <div class="radio-group">
              <label class="radio-label">
                <input
                  type="radio"
                  v-model="uploadForm.category"
                  value="group"
                />
                <span class="radio-text">
                  <span class="category-badge group">그룹사</span>
                  사내 그룹사용 템플릿
                </span>
              </label>
              <label class="radio-label">
                <input
                  type="radio"
                  v-model="uploadForm.category"
                  value="customer"
                />
                <span class="radio-text">
                  <span class="category-badge customer">고객사</span>
                  외부 고객사용 템플릿
                </span>
              </label>
            </div>
          </div>

          <div class="form-group">
            <label>설명 (선택)</label>
            <textarea
              v-model="uploadForm.description"
              placeholder="템플릿에 대한 설명을 입력하세요"
              rows="3"
            ></textarea>
          </div>

          <div class="form-group checkbox-group">
            <input
              type="checkbox"
              id="is-default"
              v-model="uploadForm.isDefault"
            />
            <label for="is-default">기본 템플릿으로 설정</label>
          </div>

          <div v-if="uploadError" class="error-message">
            {{ uploadError }}
          </div>

          <div v-if="uploadSuccess" class="success-message">
            {{ uploadSuccess }}
          </div>
        </div>

        <div class="modal-footer">
          <button class="cancel-btn" @click="closeUploadModal">취소</button>
          <button
            class="submit-btn"
            @click="handleUpload"
            :disabled="templateStore.uploading"
          >
            {{ templateStore.uploading ? '업로드 중...' : '업로드' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.templates-page {
  padding: var(--spacing-lg) 0;
}

.page-header {
  margin-bottom: var(--spacing-2xl);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.page-header h1 {
  font-size: 2.5rem;
  margin-bottom: var(--spacing-sm);
}

.page-description {
  color: var(--color-text-secondary);
  font-size: 1.125rem;
}

/* 필터 탭 */
.filter-tabs {
  display: flex;
  gap: 8px;
  margin-top: var(--spacing-lg);
}

.filter-tab {
  padding: 8px 16px;
  background: var(--color-surface);
  border: 1px solid #e0e0e0;
  border-radius: 20px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-tab:hover {
  border-color: var(--color-primary);
}

.filter-tab.active {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: white;
}

.filter-tab.active .category-badge {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

/* 카테고리 뱃지 */
.category-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.category-badge.group {
  background: #e3f2fd;
  color: #1565c0;
}

.category-badge.customer {
  background: #e8f5e9;
  color: #2e7d32;
}

.upload-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.upload-btn:hover {
  background: var(--color-primary-dark);
}

.upload-icon {
  font-size: 1.25rem;
  font-weight: bold;
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
  margin-bottom: var(--spacing-lg);
}

.upload-btn-large {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 16px 32px;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1.125rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.upload-btn-large:hover {
  background: var(--color-primary-dark);
}

/* 모달 스타일 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #eee;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.25rem;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #666;
  padding: 0;
  line-height: 1;
}

.close-btn:hover {
  color: #333;
}

.modal-body {
  padding: 24px;
}

.modal-description {
  color: #666;
  margin-bottom: 24px;
  font-size: 0.9rem;
  line-height: 1.6;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
}

.form-group input[type="text"],
.form-group textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.2s;
}

.form-group input[type="text"]:focus,
.form-group textarea:focus {
  outline: none;
  border-color: var(--color-primary);
}

.file-input-wrapper {
  position: relative;
}

.file-input-wrapper input[type="file"] {
  position: absolute;
  opacity: 0;
  width: 100%;
  height: 100%;
  cursor: pointer;
}

.file-input-label {
  display: block;
  padding: 12px;
  border: 2px dashed #ddd;
  border-radius: 8px;
  text-align: center;
  color: #666;
  cursor: pointer;
  transition: border-color 0.2s, background-color 0.2s;
}

.file-input-label:hover {
  border-color: var(--color-primary);
  background-color: #f8f9fa;
}

/* 라디오 그룹 */
.radio-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.radio-label {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.radio-label:hover {
  border-color: var(--color-primary);
  background: #f8f9fa;
}

.radio-label:has(input:checked) {
  border-color: var(--color-primary);
  background: #f0f7ff;
}

.radio-label input[type="radio"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: var(--color-primary);
}

.radio-text {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.95rem;
}

.checkbox-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.checkbox-group input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.checkbox-group label {
  margin-bottom: 0;
  cursor: pointer;
}

.error-message {
  background: #fee;
  color: #c00;
  padding: 12px;
  border-radius: 8px;
  margin-top: 16px;
}

.success-message {
  background: #efe;
  color: #060;
  padding: 12px;
  border-radius: 8px;
  margin-top: 16px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid #eee;
}

.cancel-btn {
  padding: 10px 20px;
  background: #f0f0f0;
  color: #333;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.cancel-btn:hover {
  background: #e0e0e0;
}

.submit-btn {
  padding: 10px 20px;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.submit-btn:hover:not(:disabled) {
  background: var(--color-primary-dark);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
