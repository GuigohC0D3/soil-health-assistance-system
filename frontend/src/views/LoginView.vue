<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-brand">
        <div class="auth-logo">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 22V12"/>
            <path d="M5 12C5 7 8 3 12 3c4 0 7 4 7 9"/>
            <path d="M5 12c2-1 5-2 7-2s5 1 7 2"/>
          </svg>
        </div>
        <h1>Sistema de Saúde do Solo</h1>
        <p>Entre com suas credenciais para continuar</p>
      </div>

      <form @submit.prevent="handleLogin">
        <div v-if="error" class="alert alert-error">{{ error }}</div>

        <div class="form-group">
          <label class="form-label">E-mail</label>
          <input v-model="form.email" type="email" class="form-control" placeholder="seu@email.com" required />
        </div>

        <div class="form-group">
          <label class="form-label">Senha</label>
          <input v-model="form.senha" type="password" class="form-control" placeholder="••••••••" required />
        </div>

        <button type="submit" class="btn btn-primary w-full" :disabled="loading">
          {{ loading ? 'Entrando...' : 'Entrar' }}
        </button>
      </form>

      <p class="auth-footer">
        Não tem conta? <RouterLink to="/register">Cadastre-se</RouterLink>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

const form = ref({ email: '', senha: '' })
const loading = ref(false)
const error = ref('')

async function handleLogin() {
  loading.value = true
  error.value = ''
  try {
    await auth.login(form.value)
    router.push('/dashboard')
  } catch (e: any) {
    error.value = e.response?.data?.detail ?? 'Erro ao fazer login'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  background: linear-gradient(135deg, var(--color-primary-dark) 0%, var(--color-primary) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}
.auth-card {
  background: var(--color-surface);
  border-radius: 12px;
  padding: 36px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 20px 40px rgba(0,0,0,0.2);
}
.auth-brand { text-align: center; margin-bottom: 28px; }
.auth-logo {
  width: 52px;
  height: 52px;
  background: var(--color-primary);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 12px;
}
.auth-logo svg { width: 28px; height: 28px; color: #fff; }
.auth-brand h1 { font-size: 18px; font-weight: 700; color: var(--color-primary-dark); }
.auth-brand p { font-size: 13px; color: var(--color-text-muted); margin-top: 4px; }
.w-full { width: 100%; justify-content: center; }
.auth-footer { text-align: center; margin-top: 20px; font-size: 13px; color: var(--color-text-muted); }
</style>
