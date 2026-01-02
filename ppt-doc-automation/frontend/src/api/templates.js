import apiClient from './index'

export const templatesApi = {
    /**
     * 템플릿 목록 조회
     */
    getAll: (params = {}) => {
        return apiClient.get('/templates', { params })
    },

    /**
     * 템플릿 상세 조회
     */
    getById: (id) => {
        return apiClient.get(`/templates/${id}`)
    },

    /**
     * 템플릿 생성
     */
    create: (data) => {
        return apiClient.post('/templates', data)
    },

    /**
     * 템플릿 수정
     */
    update: (id, data) => {
        return apiClient.put(`/templates/${id}`, data)
    },

    /**
     * 템플릿 삭제
     */
    delete: (id) => {
        return apiClient.delete(`/templates/${id}`)
    },

    /**
     * 템플릿 파일 업로드
     */
    upload: (file, name, description) => {
        const formData = new FormData()
        formData.append('file', file)

        return apiClient.post('/templates/upload', formData, {
            params: { name, description },
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        })
    },
}
