import { defineStore } from 'pinia'
import { ref } from 'vue'
import { templatesApi } from '@/api/templates'

export const useTemplateStore = defineStore('template', () => {
    const templates = ref([])
    const currentTemplate = ref(null)
    const loading = ref(false)
    const uploading = ref(false)
    const error = ref(null)

    async function fetchTemplates() {
        loading.value = true
        error.value = null
        try {
            const response = await templatesApi.getAll()
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

    async function uploadTemplate(file, name, description = '', isDefault = false) {
        uploading.value = true
        error.value = null
        try {
            const response = await templatesApi.upload(file, name, description, isDefault)
            // 업로드 성공 후 목록 새로고침
            await fetchTemplates()
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
