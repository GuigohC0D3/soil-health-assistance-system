import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/dashboard' },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
      meta: { guest: true },
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/RegisterView.vue'),
      meta: { guest: true },
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: () => import('@/views/DashboardView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/properties',
      name: 'properties',
      component: () => import('@/views/PropertiesView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/properties/new',
      name: 'property-new',
      component: () => import('@/views/PropertyFormView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/properties/:id/edit',
      name: 'property-edit',
      component: () => import('@/views/PropertyFormView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/analyses',
      name: 'analyses',
      component: () => import('@/views/AnalysisHistoryView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/analyses/new',
      name: 'analysis-new',
      component: () => import('@/views/SoilAnalysisFormView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/analyses/:id/edit',
      name: 'analysis-edit',
      component: () => import('@/views/SoilAnalysisFormView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/recommendations',
      name: 'recommendations',
      component: () => import('@/views/RecommendationsView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/report',
      name: 'report',
      component: () => import('@/views/ReportView.vue'),
      meta: { requiresAuth: true },
    },
  ],
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.isAuthenticated) return '/login'
  if (to.meta.guest && auth.isAuthenticated) return '/dashboard'
})

export default router
