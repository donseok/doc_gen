import { defineStore } from 'pinia'
import { ref } from 'vue'
import { templatesApi } from '@/api/templates'

export const useTemplateStore = defineStore('template', () => {
    const templates = ref([])
    const currentTemplate = ref(null)
    const loading = ref(false)
    const uploading = ref(false)
    const error = ref(null)
    const currentCategory = ref(null) // null: 전체, 'group': 그룹사, 'customer': 고객사

    async function fetchTemplates(category = null) {
        loading.value = true
        error.value = null
        currentCategory.value = category
        try {
            const params = {}
            if (category) {
                params.category = category
            }
            const response = await templatesApi.getAll(params)
            templates.value = response.items || []
        } catch (err) {
            error.value = err.message
            templates.value = []
        } finally {
            loading.value = false
        }
    }

    async function fetchTemplate(id) {
        loading.value = true
        error.value = null
        try {
            currentTemplate.value = await templatesApi.getById(id)
        } catch (err) {
            error.value = err.message
            currentTemplate.value = null
        } finally {
            loading.value = false
        }
    }

    async function uploadTemplate(file, name, description = '', category = 'group', isDefault = false) {
        uploading.value = true
        error.value = null
        try {
            const response = await templatesApi.upload(file, name, description, category, isDefault)
            // 업로드 성공 후 목록 새로고침 (현재 필터 유지)
            await fetchTemplates(currentCategory.value)
            return response
        } catch (err) {
            error.value = err.response?.data?.detail || err.message
            throw err
        } finally {
            uploading.value = false
        }
    }

    async function deleteTemplate(id) {
        loading.value = true
        error.value = null
        try {
            await templatesApi.delete(id)
            // 삭제 성공 후 목록 새로고침
            await fetchTemplates()
        } catch (err) {
            error.value = err.response?.data?.detail || err.message
            throw err
        } finally {
            loading.value = false
        }
    }

    function clearCurrentTemplate() {
        currentTemplate.value = null
    }

    return {
        templates,
        currentTemplate,
        currentCategory,
        loading,
        uploading,
        error,
        fetchTemplates,
        fetchTemplate,
        uploadTemplate,
        deleteTemplate,
        clearCurrentTemplate,
    }
})
