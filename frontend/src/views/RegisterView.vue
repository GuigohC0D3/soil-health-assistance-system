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
        <h1>Criar Conta</h1>
        <p>Cadastre-se para usar o sistema</p>
      </div>

      <form @submit.prevent="handleRegister">
        <div v-if="error" class="alert alert-error">{{ error }}</div>
        <div v-if="success" class="alert alert-success">{{ success }}</div>

        <div class="form-group">
          <label class="form-label">Nome completo</label>
          <input v-model="form.nome" type="text" class="form-control" placeholder="João da Silva" required />
        </div>

        <div class="form-group">
          <label class="form-label">E-mail</label>
          <input v-model="form.email" type="email" class="form-control" placeholder="seu@email.com" required />
        </div>

        <div class="form-group">
          <label class="form-label">Senha</label>
          <input v-model="form.senha" type="password" class="form-control" placeholder="Mínimo 6 caracteres" required minlength="6" />
        </div>

        <div class="form-group">
          <label class="form-label">Perfil</label>
          <select v-model="form.papel" class="form-control">
            <option value="produtor">Produtor Rural</option>
            <option value="tecnico">Técnico Agrícola</option>
          </select>
        </div>

        <button type="submit" class="btn btn-primary w-full" :disabled="loading">
          {{ loading ? 'Cadastrando...' : 'Criar Conta' }}
        </button>
      </form>

      <p class="auth-footer">
        Já tem conta? <RouterLink to="/login">Entrar</RouterLink>
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

const form = ref({ nome: '', email: '', senha: '', papel: 'produtor' as const })
const loading = ref(false)
const error = ref('')
const success = ref('')

async function handleRegister() {
  loading.value = true
  error.value = ''
  success.value = ''
  try {
    await auth.register(form.value)
    success.value = 'Conta criada! Redirecionando para o login...'
    setTimeout(() => router.push('/login'), 1500)
  } catch (e: any) {
    error.value = e.response?.data?.detail ?? 'Erro ao criar conta'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  background: var(--color-bg);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

.auth-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  padding: 40px 36px;
  width: 100%;
  max-width: 420px;
  box-shadow: var(--shadow-md);
}

.auth-brand { text-align: center; margin-bottom: 28px; }

.auth-logo {
  width: 48px;
  height: 48px;
  background: var(--color-primary-light);
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 14px;
}
.auth-logo svg { width: 24px; height: 24px; color: var(--color-primary); }

.auth-brand h1 {
  font-size: 17px;
  font-weight: 700;
  color: var(--color-text);
  letter-spacing: -0.02em;
}
.auth-brand p { font-size: 13px; color: var(--color-text-muted); margin-top: 4px; }

.w-full { width: 100%; justify-content: center; }

.auth-footer {
  text-align: center;
  margin-top: 20px;
  font-size: 13px;
  color: var(--color-text-muted);
}
</style>
