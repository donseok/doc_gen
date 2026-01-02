import apiClient from './index'

export const documentsApi = {
    /**
     * 문서 목록 조회
     */
    getAll: (params = {}) => {
        return apiClient.get('/documents', { params })
    },

    /**
     * 문서 상세 조회
     */
    getById: (id) => {
        return apiClient.get(`/documents/${id}`)
    },

    /**
     * 문서 삭제
     */
    delete: (id) => {
        return apiClient.delete(`/documents/${id}`)
    },

    /**
     * 문서 다운로드
     */
    download: async (id) => {
        const response = await fetch(`/api/documents/${id}/download`)

        if (!response.ok) {
            throw new Error('다운로드에 실패했습니다.')
        }

        const blob = await response.blob()
        const contentDisposition = response.headers.get('content-disposition')
        let filename = 'document.pptx'

        if (contentDisposition) {
            const match = contentDisposition.match(/filename="?(.+)"?/)
            if (match) {
                filename = match[1]
            }
        }

        // 다운로드 링크 생성
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = filename
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
    },
}
