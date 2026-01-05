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
     * @param {File} file - PPTX 파일
     * @param {string} name - 템플릿 이름
     * @param {string} description - 설명
     * @param {string} category - 카테고리 (group: 그룹사, customer: 고객사)
     * @param {boolean} isDefault - 기본 템플릿 여부
     */
    upload: (file, name, description = '', category = 'group', isDefault = false) => {
        const formData = new FormData()
        formData.append('file', file)
        formData.append('name', name)
        if (description) {
            formData.append('description', description)
        }
        formData.append('category', category)
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
