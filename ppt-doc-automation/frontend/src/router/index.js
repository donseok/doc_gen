import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/',
            name: 'home',
            component: HomeView,
        },
        {
            path: '/templates',
            name: 'templates',
            component: () => import('@/views/TemplatesView.vue'),
        },
        {
            path: '/generate',
            name: 'generate',
            component: () => import('@/views/GenerateView.vue'),
        },
        {
            path: '/documents',
            name: 'documents',
            component: () => import('@/views/DocumentsView.vue'),
        },
    ],
})

export default router
