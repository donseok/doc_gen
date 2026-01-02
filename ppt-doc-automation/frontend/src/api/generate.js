import apiClient from './index'

export const generateApi = {
    /**
     * 텍스트(마크다운)로부터 PPT 생성
     */
    fromText: (mdContent, templateId = null, options = {}) => {
        return apiClient.post('/generate/from-text', {
            md_content: mdContent,
            template_id: templateId,
            options,
        })
    },

    /**
     * 파일로부터 PPT 생성
     */
    fromFile: (file, templateId = null) => {
        const formData = new FormData()
        formData.append('file', file)

        let url = '/generate/from-file'
        if (templateId) {
            url += `?template_id=${templateId}`
        }

        return apiClient.post(url, formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        })
    },
}
