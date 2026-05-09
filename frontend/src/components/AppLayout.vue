<template>
  <div class="layout">
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
        <RouterLink to="/fertilizer" class="nav-item" active-class="active" @click="sidebarOpen = false">
          <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="2" y="7" width="20" height="14" rx="2"/>
            <path d="M16 7V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v2"/>
            <line x1="12" y1="12" x2="12" y2="17"/>
            <line x1="9.5" y1="14.5" x2="14.5" y2="14.5"/>
          </svg>
          Calculadora
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
      <!-- Topbar fica fora do scroll para o dropdown não ser cortado -->
      <div class="topbar">
        <button class="hamburger" @click="sidebarOpen = !sidebarOpen" aria-label="Abrir menu">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="20" height="20">
            <line x1="3" y1="6" x2="21" y2="6"/>
            <line x1="3" y1="12" x2="21" y2="12"/>
            <line x1="3" y1="18" x2="21" y2="18"/>
          </svg>
        </button>

        <!-- Notification Bell -->
        <div class="notif-area" v-click-outside="closeBell">
          <button class="notif-bell" @click="bellOpen = !bellOpen" aria-label="Notificações">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="18" height="18">
              <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
              <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
            </svg>
            <span
              v-if="notifications.totalCount > 0"
              class="notif-badge"
              :class="{ 'notif-badge--danger': notifications.criticalCount > 0 }"
            >
              {{ notifications.totalCount > 9 ? '9+' : notifications.totalCount }}
            </span>
          </button>

          <div v-if="bellOpen" class="notif-dropdown">
            <div class="notif-header">
              <span>Alertas do Sistema</span>
              <span class="notif-count">{{ notifications.totalCount }}</span>
            </div>
            <div v-if="notifications.alerts.length === 0" class="notif-empty">
              Nenhum alerta ativo.
            </div>
            <div v-else class="notif-list">
              <div
                v-for="(alert, i) in notifications.alerts"
                :key="i"
                class="notif-item"
                :class="{ 'notif-item--alta': alert.prioridade === 'alta' }"
                @click="navigateAlert(alert)"
              >
                <span class="notif-dot" :class="alert.prioridade === 'alta' ? 'dot-alta' : 'dot-media'" />
                <span class="notif-msg">{{ alert.mensagem }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Área scrollável separada da topbar -->
      <div class="content-scroll">
        <slot />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useNotificationsStore } from '@/stores/notifications'
import type { AlertItem } from '@/types'

const auth = useAuthStore()
const notifications = useNotificationsStore()
const router = useRouter()
const sidebarOpen = ref(false)
const bellOpen = ref(false)

onMounted(() => { if (!notifications.loaded) notifications.fetchAlerts() })

const userInitial = computed(() => auth.user?.nome?.[0]?.toUpperCase() ?? '?')
const roleLabel = computed(() => {
  const map: Record<string, string> = { produtor: 'Produtor Rural', tecnico: 'Técnico Agrícola', admin: 'Administrador' }
  return map[auth.user?.papel ?? ''] ?? ''
})

function closeBell() { bellOpen.value = false }

function navigateAlert(alert: AlertItem) {
  notifications.dismiss(alert)
  bellOpen.value = false
  if (alert.analise_id) {
    router.push(`/analyses?propriedade_id=${alert.propriedade_id}`)
  } else {
    router.push('/properties')
  }
}

function handleLogout() {
  auth.logout()
  notifications.clear()
  router.push('/login')
}
</script>

<style scoped>
.layout {
  display: flex;
  min-height: 100vh;
}

/* ─── Sidebar ─── */
.sidebar {
  width: 240px;
  min-width: 240px;
  background: #0f172a;
  display: flex;
  flex-direction: column;
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 20px 16px 18px;
  border-bottom: 1px solid rgba(255,255,255,0.06);
}
.brand-icon { width: 20px; height: 20px; color: #4ade80; flex-shrink: 0; }
.brand-name { color: #f8fafc; font-weight: 700; font-size: 14.5px; letter-spacing: -0.01em; }

.sidebar-nav {
  flex: 1;
  padding: 10px 8px;
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 9px 12px;
  border-radius: 8px;
  color: #94a3b8;
  font-size: 13.5px;
  font-weight: 500;
  text-decoration: none;
  transition: background 0.12s, color 0.12s;
  letter-spacing: -0.01em;
}
.nav-item:hover { background: rgba(255,255,255,0.06); color: #e2e8f0; text-decoration: none; }
.nav-item.active {
  background: rgba(74, 222, 128, 0.12);
  color: #4ade80;
}
.nav-icon { width: 15px; height: 15px; flex-shrink: 0; }

.sidebar-footer {
  padding: 14px 16px;
  border-top: 1px solid rgba(255,255,255,0.06);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}
.user-info { display: flex; align-items: center; gap: 10px; overflow: hidden; min-width: 0; }
.user-avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: rgba(74, 222, 128, 0.2);
  color: #4ade80;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 13px;
  flex-shrink: 0;
}
.user-name { color: #e2e8f0; font-size: 13px; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.user-role { color: #64748b; font-size: 11px; }

.btn-logout {
  background: transparent;
  border: none;
  color: #475569;
  cursor: pointer;
  padding: 6px;
  flex-shrink: 0;
  transition: color 0.12s, background 0.12s;
  display: flex;
  align-items: center;
  border-radius: 6px;
}
.btn-logout:hover { color: #e2e8f0; background: rgba(255,255,255,0.06); }

/* ─── Main content ─── */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  max-height: 100vh;
  min-width: 0;
  /* sem overflow aqui para o dropdown não ser cortado */
}

.topbar {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  padding: 20px 32px 0;
  position: relative;
  z-index: 100;
  flex-shrink: 0;
}

.content-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 16px 32px 32px;
}

.hamburger {
  display: none;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 4px;
  color: var(--color-text-muted);
  border-radius: 6px;
}
.hamburger:hover { background: var(--color-surface-2); }

/* ─── Notification Bell ─── */
.notif-area { position: relative; }

.notif-bell {
  position: relative;
  background: transparent;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  padding: 7px 9px;
  cursor: pointer;
  color: var(--color-text-muted);
  display: flex;
  align-items: center;
  transition: background 0.12s, color 0.12s;
}
.notif-bell:hover { background: var(--color-surface-2); color: var(--color-text); }

.notif-badge {
  position: absolute;
  top: -5px;
  right: -5px;
  background: #f59e0b;
  color: #fff;
  font-size: 10px;
  font-weight: 700;
  border-radius: 99px;
  padding: 1px 5px;
  min-width: 18px;
  text-align: center;
  line-height: 1.4;
}
.notif-badge--danger { background: #ef4444; }

.notif-dropdown {
  position: absolute;
  right: 0;
  top: calc(100% + 8px);
  width: 320px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg, 10px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.12);
  z-index: 300;
  overflow: hidden;
}

.notif-header {
  padding: 12px 16px;
  font-weight: 600;
  font-size: 13px;
  border-bottom: 1px solid var(--color-border);
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.notif-count {
  background: var(--color-surface-2);
  border-radius: 99px;
  padding: 1px 8px;
  font-size: 11px;
  font-weight: 600;
}

.notif-empty { padding: 20px 16px; color: var(--color-text-muted); font-size: 13px; text-align: center; }

.notif-list { max-height: 300px; overflow-y: auto; }

.notif-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 10px 16px;
  cursor: pointer;
  border-bottom: 1px solid var(--color-border);
  transition: background 0.1s;
}
.notif-item:last-child { border-bottom: none; }
.notif-item:hover { background: var(--color-surface-2); }
.notif-item--alta { border-left: 3px solid #ef4444; }

.notif-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
  margin-top: 4px;
}
.dot-alta { background: #ef4444; }
.dot-media { background: #f59e0b; }

.notif-msg { font-size: 12.5px; line-height: 1.5; color: var(--color-text); flex: 1; min-width: 0; word-break: break-word; }

.sidebar-overlay { display: none; }

@media (max-width: 768px) {
  .layout { position: relative; }

  .sidebar {
    position: fixed;
    top: 0;
    left: 0;
    height: 100vh;
    z-index: 200;
    transform: translateX(-100%);
    transition: transform 0.22s ease;
  }
  .sidebar.sidebar-open { transform: translateX(0); }

  .sidebar-overlay {
    display: block;
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.5);
    z-index: 199;
  }

  .topbar { padding: 12px 16px 0; justify-content: space-between; }
  .content-scroll { padding: 12px 16px 16px; }

  .hamburger {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .notif-dropdown { width: 280px; right: -8px; }
}
</style>
