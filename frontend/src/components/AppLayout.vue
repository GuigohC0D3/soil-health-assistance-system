<template>
  <div class="layout">
    <!-- overlay para fechar o menu em mobile -->
    <div v-if="sidebarOpen" class="sidebar-overlay" @click="sidebarOpen = false" />

    <aside class="sidebar" :class="{ 'sidebar-open': sidebarOpen }">
      <div class="sidebar-brand">
        <svg class="brand-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 22V12"/>
          <path d="M5 12C5 7 8 3 12 3c4 0 7 4 7 9"/>
          <path d="M5 12c2-1 5-2 7-2s5 1 7 2"/>
        </svg>
        <span class="brand-name">Saúde do Solo</span>
      </div>

      <nav class="sidebar-nav">
        <RouterLink to="/dashboard" class="nav-item" active-class="active" @click="sidebarOpen = false">
          <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/>
            <rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/>
          </svg>
          Dashboard
        </RouterLink>
        <RouterLink to="/properties" class="nav-item" active-class="active" @click="sidebarOpen = false">
          <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
            <polyline points="9 22 9 12 15 12 15 22"/>
          </svg>
          Propriedades
        </RouterLink>
        <RouterLink to="/analyses" class="nav-item" active-class="active" @click="sidebarOpen = false">
          <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M9 3H5a2 2 0 0 0-2 2v4m6-6h10a2 2 0 0 1 2 2v4M9 3v11m0 0l3 3m-3-3l-3 3m12-14v11m0 0l3 3m-3-3l-3 3"/>
          </svg>
          Análises de Solo
        </RouterLink>
        <RouterLink to="/recommendations" class="nav-item" active-class="active" @click="sidebarOpen = false">
          <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
          Recomendações
        </RouterLink>
        <RouterLink to="/report" class="nav-item" active-class="active" @click="sidebarOpen = false">
          <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
            <line x1="16" y1="13" x2="8" y2="13"/>
            <line x1="16" y1="17" x2="8" y2="17"/>
            <polyline points="10 9 9 9 8 9"/>
          </svg>
          Relatórios
        </RouterLink>
      </nav>

      <div class="sidebar-footer">
        <div class="user-info">
          <div class="user-avatar">{{ userInitial }}</div>
          <div>
            <div class="user-name">{{ auth.user?.nome }}</div>
            <div class="user-role">{{ roleLabel }}</div>
          </div>
        </div>
        <button class="btn-logout" @click="handleLogout" title="Sair">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
            <polyline points="16 17 21 12 16 7"/>
            <line x1="21" y1="12" x2="9" y2="12"/>
          </svg>
        </button>
      </div>
    </aside>

    <main class="main-content">
      <button class="hamburger" @click="sidebarOpen = !sidebarOpen" aria-label="Abrir menu">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="20" height="20">
          <line x1="3" y1="6" x2="21" y2="6"/>
          <line x1="3" y1="12" x2="21" y2="12"/>
          <line x1="3" y1="18" x2="21" y2="18"/>
        </svg>
      </button>
      <slot />
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()
const sidebarOpen = ref(false)

const userInitial = computed(() => auth.user?.nome?.[0]?.toUpperCase() ?? '?')
const roleLabel = computed(() => {
  const map: Record<string, string> = { produtor: 'Produtor Rural', tecnico: 'Técnico Agrícola', admin: 'Administrador' }
  return map[auth.user?.papel ?? ''] ?? ''
})

function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.layout {
  display: flex;
  min-height: 100vh;
}

.sidebar {
  width: 230px;
  min-width: 230px;
  background: var(--color-primary-dark);
  display: flex;
  flex-direction: column;
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 20px 16px;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}
.brand-icon { width: 22px; height: 22px; color: var(--color-secondary); flex-shrink: 0; }
.brand-name { color: #fff; font-weight: 700; font-size: 15px; }

.sidebar-nav {
  flex: 1;
  padding: 12px 8px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 6px;
  color: rgba(255,255,255,0.75);
  font-size: 14px;
  font-weight: 500;
  text-decoration: none;
  transition: background 0.15s, color 0.15s;
}
.nav-item:hover { background: rgba(255,255,255,0.08); color: #fff; text-decoration: none; }
.nav-item.active { background: var(--color-primary); color: #fff; }
.nav-icon { width: 16px; height: 16px; flex-shrink: 0; }

.sidebar-footer {
  padding: 16px;
  border-top: 1px solid rgba(255,255,255,0.1);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}
.user-info { display: flex; align-items: center; gap: 10px; overflow: hidden; }
.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--color-primary-light);
  color: var(--color-primary-dark);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 14px;
  flex-shrink: 0;
}
.user-name { color: #fff; font-size: 13px; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.user-role { color: rgba(255,255,255,0.5); font-size: 11px; }

.btn-logout {
  background: transparent;
  border: none;
  color: rgba(255,255,255,0.5);
  cursor: pointer;
  padding: 6px;
  flex-shrink: 0;
  transition: color 0.15s;
  display: flex;
  align-items: center;
  border-radius: 4px;
}
.btn-logout:hover { color: #fff; background: rgba(255,255,255,0.08); }

.main-content {
  flex: 1;
  padding: 28px;
  overflow-y: auto;
  max-height: 100vh;
  min-width: 0;
}

.hamburger {
  display: none;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 4px;
  margin-bottom: 16px;
  color: var(--color-primary-dark);
  border-radius: 4px;
}
.hamburger:hover { background: var(--color-border); }

.sidebar-overlay {
  display: none;
}

@media (max-width: 768px) {
  .layout {
    position: relative;
  }

  .sidebar {
    position: fixed;
    top: 0;
    left: 0;
    height: 100vh;
    z-index: 200;
    transform: translateX(-100%);
    transition: transform 0.25s ease;
  }

  .sidebar.sidebar-open {
    transform: translateX(0);
  }

  .sidebar-overlay {
    display: block;
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.4);
    z-index: 199;
  }

  .main-content {
    padding: 16px;
    max-height: 100vh;
  }

  .hamburger {
    display: flex;
    align-items: center;
    justify-content: center;
  }
}
</style>
