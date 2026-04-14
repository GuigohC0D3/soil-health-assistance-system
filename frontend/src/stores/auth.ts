import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'
import type { User, LoginRequest, RegisterRequest, TokenResponse } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(JSON.parse(localStorage.getItem('user') || 'null'))
  const token = ref<string | null>(localStorage.getItem('access_token'))

  const isAuthenticated = computed(() => !!token.value)

  async function login(credentials: LoginRequest): Promise<void> {
    const { data } = await api.post<TokenResponse>('/api/auth/login', credentials)
    token.value = data.access_token
    user.value = data.user
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('user', JSON.stringify(data.user))
  }

  async function register(payload: RegisterRequest): Promise<void> {
    await api.post('/api/auth/register', payload)
  }

  function logout(): void {
    token.value = null
    user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
  }

  return { user, token, isAuthenticated, login, register, logout }
})
