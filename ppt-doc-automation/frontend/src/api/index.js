import axios from 'axios'

const apiClient = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
    headers: {
        'Content-Type': 'application/json',
    },
    timeout: 30000,
})

// 요청 인터셉터
apiClient.interceptors.request.use(
    (config) => {
        // 인증 토큰 추가 등 필요시 처리
        return config
    },
    (error) => {
        return Promise.reject(error)
    }
)

// 응답 인터셉터
apiClient.interceptors.response.use(
    (response) => {
        return response.data
    },
    (error) => {
        const message = error.response?.data?.detail || error.message || '요청 처리 중 오류가 발생했습니다.'
        return Promise.reject(new Error(message))
    }
)

export default apiClient
