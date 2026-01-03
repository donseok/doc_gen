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
    upload: (file, name, description = '', isDefault = false) => {
        const formData = new FormData()
        formData.append('file', file)
        formData.append('name', name)
        if (description) {
            formData.append('description', description)
        }
        formData.append('is_default', isDefault)

        return apiClient.post('/templates/upload', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        })
    },

    /**
     * 템플릿 스타일 정보 조회
     */
    getStyle: (id) => {
        return apiClient.get(`/templates/${id}/style`)
    },
}
