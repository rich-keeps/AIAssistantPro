import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
    history: createWebHistory(),
    routes: [
        {
            path: '/',
            redirect: '/excel-processor'
        },
        {
            path: '/excel-processor',
            name: 'excel-processor',
            component: () => import('../views/ExcelProcessor.vue')
        },
        {
            path: '/report',
            name: 'report',
            component: () => import('../views/Report.vue')
        },
        {
            path: '/settings',
            name: 'settings',
            component: () => import('../views/Settings.vue')
        }
    ]
})

export default router 