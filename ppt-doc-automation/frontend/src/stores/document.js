import { defineStore } from 'pinia'
import { ref } from 'vue'
import { documentsApi } from '@/api/documents'

export const useDocumentStore = defineStore('document', () => {
    const documents = ref([])
    const currentDocument = ref(null)
    const loading = ref(false)
    const error = ref(null)

    async function fetchDocuments() {
        loading.value = true
        error.value = null
        try {
            const response = await documentsApi.getAll()
            documents.value = response.items || []
        } catch (err) {
            error.value = err.message
            documents.value = []
        } finally {
            loading.value = false
        }
    }

    async function fetchDocument(id) {
        loading.value = true
        error.value = null
        try {
            currentDocument.value = await documentsApi.getById(id)
        } catch (err) {
            error.value = err.message
            currentDocument.value = null
        } finally {
            loading.value = false
        }
    }

    function addDocument(doc) {
        documents.value.unshift(doc)
    }

    async function deleteDocument(id) {
        try {
            await documentsApi.delete(id)
            documents.value = documents.value.filter(d => d.id !== id)
        } catch (err) {
            error.value = err.message
        }
    }

    function clearCurrentDocument() {
        currentDocument.value = null
    }

    return {
        documents,
        currentDocument,
        loading,
        error,
        fetchDocuments,
        fetchDocument,
        addDocument,
        deleteDocument,
        clearCurrentDocument,
    }
})
