<template>
  <AppLayout>
    <div class="page-header">
      <div>
        <h2 class="page-title">Propriedades</h2>
        <p class="page-subtitle">Gerencie suas propriedades agrícolas</p>
      </div>
      <RouterLink to="/properties/new" class="btn btn-primary">+ Nova Propriedade</RouterLink>
    </div>

    <div v-if="error" class="alert alert-error">{{ error }}</div>

    <div v-if="loading" class="empty-state">
      <div class="empty-state-desc">Carregando...</div>
    </div>

    <div v-else-if="properties.length === 0" class="empty-state">
      <div class="empty-state-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
          <polyline points="9 22 9 12 15 12 15 22"/>
        </svg>
      </div>
      <div class="empty-state-title">Nenhuma propriedade cadastrada</div>
      <div class="empty-state-desc">Cadastre sua primeira propriedade para começar.</div>
    </div>

    <div v-else class="grid-2">
      <div v-for="p in properties" :key="p.id" class="card property-card">
        <div class="card-body">
          <div class="prop-header">
            <h3 class="prop-name">{{ p.nome }}</h3>
            <div class="prop-actions">
              <RouterLink :to="`/properties/${p.id}/edit`" class="btn btn-ghost btn-sm">Editar</RouterLink>
              <button class="btn btn-danger btn-sm" @click="confirmDelete(p)">Excluir</button>
            </div>
          </div>
          <div class="prop-details">
            <div v-if="p.area_hectares" class="prop-detail">
              <span class="detail-label">Área</span>
              <span>{{ p.area_hectares.toLocaleString('pt-BR') }} ha</span>
            </div>
            <div v-if="p.cidade || p.estado" class="prop-detail">
              <span class="detail-label">Localização</span>
              <span>{{ [p.cidade, p.estado].filter(Boolean).join(' - ') }}</span>
            </div>
            <div v-if="p.localizacao" class="prop-detail">
              <span class="detail-label">Endereço</span>
              <span>{{ p.localizacao }}</span>
            </div>
          </div>
          <div class="prop-footer">
            <RouterLink :to="`/analyses?propriedade_id=${p.id}`" class="btn btn-ghost btn-sm">
              Ver análises
            </RouterLink>
          </div>
        </div>
      </div>
    </div>

    <div v-if="deleteTarget" class="modal-overlay" @click.self="deleteTarget = null">
      <div class="modal">
        <h3>Excluir propriedade?</h3>
        <p>Tem certeza que deseja excluir <strong>{{ deleteTarget.nome }}</strong>? Esta ação também removerá todas as análises associadas.</p>
        <div class="modal-actions">
          <button class="btn btn-secondary" @click="deleteTarget = null">Cancelar</button>
          <button class="btn btn-danger" @click="handleDelete" :disabled="deleting">
            {{ deleting ? 'Excluindo...' : 'Excluir' }}
          </button>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import AppLayout from '@/components/AppLayout.vue'
import api from '@/services/api'
import type { Property } from '@/types'

const properties = ref<Property[]>([])
const loading = ref(true)
const error = ref('')
const deleteTarget = ref<Property | null>(null)
const deleting = ref(false)

async function load() {
  loading.value = true
  try {
    const { data } = await api.get('/api/properties/')
    properties.value = data
  } catch {
    error.value = 'Erro ao carregar propriedades'
  } finally {
    loading.value = false
  }
}

function confirmDelete(p: Property) {
  deleteTarget.value = p
}

async function handleDelete() {
  if (!deleteTarget.value) return
  deleting.value = true
  try {
    await api.delete(`/api/properties/${deleteTarget.value.id}`)
    properties.value = properties.value.filter(p => p.id !== deleteTarget.value!.id)
    deleteTarget.value = null
  } catch {
    error.value = 'Erro ao excluir propriedade'
  } finally {
    deleting.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.empty-state-icon svg { width: 40px; height: 40px; }
.property-card { transition: box-shadow 0.15s; }
.property-card:hover { box-shadow: var(--shadow-md); }
.prop-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; gap: 12px; }
.prop-name { font-size: 16px; font-weight: 600; color: var(--color-text); }
.prop-actions { display: flex; gap: 6px; flex-shrink: 0; }
.prop-details { display: flex; flex-direction: column; gap: 6px; margin-bottom: 14px; }
.prop-detail { display: flex; gap: 8px; font-size: 13px; }
.detail-label { color: var(--color-text-muted); min-width: 80px; }
.prop-footer { border-top: 1px solid var(--color-border); padding-top: 12px; }

.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; z-index: 100; }
.modal { background: var(--color-surface); border-radius: 10px; padding: 28px; max-width: 420px; width: 90%; }
.modal h3 { font-size: 17px; font-weight: 700; margin-bottom: 10px; }
.modal p { font-size: 14px; color: var(--color-text-muted); margin-bottom: 20px; line-height: 1.6; }
.modal-actions { display: flex; gap: 10px; justify-content: flex-end; }
</style>
