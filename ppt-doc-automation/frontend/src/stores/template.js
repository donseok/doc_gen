import { defineStore } from 'pinia'
import { ref } from 'vue'
import { templatesApi } from '@/api/templates'

export const useTemplateStore = defineStore('template', () => {
    const templates = ref([])
    const currentTemplate = ref(null)
    const loading = ref(false)
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

    function clearCurrentTemplate() {
        currentTemplate.value = null
    }

    return {
        templates,
        currentTemplate,
        loading,
        error,
        fetchTemplates,
        fetchTemplate,
        clearCurrentTemplate,
    }
})
