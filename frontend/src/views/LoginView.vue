<template>
  <div class="auth-page">
    <!-- Decorative background elements -->
    <div class="bg-decor" aria-hidden="true">
      <svg class="decor-blob decor-blob--tl" viewBox="0 0 400 400" xmlns="http://www.w3.org/2000/svg">
        <path d="M320,80 C380,120 420,200 380,280 C340,360 220,400 140,360 C60,320 20,220 60,140 C100,60 200,20 280,40 C300,48 312,68 320,80Z" fill="#bcaaa4" opacity="0.35"/>
      </svg>
      <svg class="decor-blob decor-blob--br" viewBox="0 0 400 400" xmlns="http://www.w3.org/2000/svg">
        <path d="M80,320 C20,280 -20,200 20,120 C60,40 180,0 260,40 C340,80 380,180 340,260 C300,340 200,380 120,360 C100,352 88,332 80,320Z" fill="#a1887f" opacity="0.25"/>
      </svg>

      <!-- Floating soil/nature icons -->
      <svg class="decor-icon decor-icon--1" viewBox="0 0 24 24" fill="none" stroke="#8d6e63" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 22V12"/><path d="M5 12C5 7 8 3 12 3c4 0 7 4 7 9"/><path d="M5 12c2-1 5-2 7-2s5 1 7 2"/>
      </svg>
      <svg class="decor-icon decor-icon--2" viewBox="0 0 24 24" fill="none" stroke="#795548" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
        <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>
      </svg>
      <svg class="decor-icon decor-icon--3" viewBox="0 0 24 24" fill="none" stroke="#6d4c41" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/><path d="M2 12h20"/>
      </svg>
      <svg class="decor-icon decor-icon--4" viewBox="0 0 24 24" fill="none" stroke="#8d6e63" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
        <path d="M17 8C8 10 5.9 16.17 3.82 19.5A1 1 0 0 0 5 21c5.25-2.5 10.17-5.5 13-13z"/><path d="M17 8L7 2"/>
      </svg>
      <svg class="decor-icon decor-icon--5" viewBox="0 0 24 24" fill="none" stroke="#a1887f" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
        <path d="M2 20h20"/><path d="M6 20V10l6-6 6 6v10"/>
      </svg>

      <!-- Ground texture lines -->
      <svg class="decor-ground" viewBox="0 0 1200 120" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none">
        <path d="M0,60 C200,20 400,100 600,60 C800,20 1000,100 1200,60 L1200,120 L0,120 Z" fill="#bcaaa4" opacity="0.18"/>
        <path d="M0,80 C300,40 600,110 900,70 C1050,52 1150,90 1200,80 L1200,120 L0,120 Z" fill="#a1887f" opacity="0.15"/>
      </svg>
    </div>

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
  background: linear-gradient(135deg, #efebe9 0%, #d7ccc8 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  position: relative;
  overflow: hidden;
}

/* Background decorative layer */
.bg-decor {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 0;
}

.decor-blob {
  position: absolute;
  width: 480px;
  height: 480px;
}
.decor-blob--tl { top: -160px; left: -160px; }
.decor-blob--br { bottom: -160px; right: -160px; }

.decor-icon {
  position: absolute;
  opacity: 0.22;
  animation: float 6s ease-in-out infinite;
}
.decor-icon--1 { width: 48px; height: 48px; top: 12%; left: 8%; animation-delay: 0s; }
.decor-icon--2 { width: 36px; height: 36px; top: 20%; right: 10%; animation-delay: 1.2s; }
.decor-icon--3 { width: 44px; height: 44px; bottom: 28%; left: 6%; animation-delay: 2.4s; }
.decor-icon--4 { width: 40px; height: 40px; top: 55%; right: 7%; animation-delay: 0.8s; }
.decor-icon--5 { width: 52px; height: 52px; bottom: 18%; right: 14%; animation-delay: 1.8s; }

.decor-ground {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 120px;
}

@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
}

/* Card */
.auth-card {
  position: relative;
  z-index: 1;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  padding: 40px 36px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 8px 32px rgba(93, 64, 55, 0.15), 0 2px 8px rgba(93, 64, 55, 0.08);
}

.auth-brand { text-align: center; margin-bottom: 32px; }

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
