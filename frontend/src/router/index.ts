import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  { path: '/', redirect: '/symmetric' },
  { path: '/symmetric', component: () => import('@/views/SymmetricView.vue') },
  { path: '/hash',      component: () => import('@/views/HashView.vue') },
  { path: '/encoding',  component: () => import('@/views/EncodingView.vue') },
  { path: '/pubkey',    component: () => import('@/views/PubkeyView.vue') },
  { path: '/demos',     component: () => import('@/views/DemosView.vue') },
  { path: '/keys',      component: () => import('@/views/KeysView.vue') },
  { path: '/audit',     component: () => import('@/views/AuditView.vue') },
  { path: '/benchmark', component: () => import('@/views/BenchmarkView.vue') },
  { path: '/login',     component: () => import('@/views/LoginView.vue') }
]

export default createRouter({
  history: createWebHistory(),
  routes
})
