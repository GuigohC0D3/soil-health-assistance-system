<template>
  <AppLayout>
    <div class="page-header">
      <div>
        <h2 class="page-title">Recomendações</h2>
        <p class="page-subtitle">Orientações de manejo geradas automaticamente</p>
      </div>
    </div>

    <div class="card filters-card">
      <div class="card-body" style="padding: 14px 20px;">
        <div class="filters-row">
          <div class="form-group" style="margin:0; min-width: 200px;">
            <label class="form-label">Propriedade</label>
            <select v-model="filterPropId" class="form-control">
              <option value="">Todas</option>
              <option v-for="p in properties" :key="p.id" :value="p.id">{{ p.nome }}</option>
            </select>
          </div>
          <div class="form-group" style="margin:0;">
            <label class="form-label">Prioridade</label>
            <select v-model="filterPriority" class="form-control">
              <option value="">Todas</option>
              <option value="alta">Alta</option>
              <option value="media">Média</option>
              <option value="baixa">Baixa</option>
            </select>
          </div>
          <button class="btn btn-secondary" style="align-self: flex-end;" @click="clearFilters">Limpar</button>
        </div>
      </div>
    </div>

    <div v-if="error" class="alert alert-error">{{ error }}</div>
    <div v-if="loading" class="empty-state"><div class="empty-state-desc">Carregando...</div></div>

    <div v-else-if="filtered.length === 0" class="empty-state">
      <div class="empty-state-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="8" x2="12" y2="12"/>
          <line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
      </div>
      <div class="empty-state-title">Nenhuma recomendação encontrada</div>
      <div class="empty-state-desc">Registre análises de solo para gerar recomendações automáticas.</div>
    </div>

    <div v-else>
      <div class="priority-summary">
        <div class="priority-chip priority-alta">
          <span class="priority-dot"></span>
          <span>Alta</span>
          <strong>{{ countByPriority('alta') }}</strong>
        </div>
        <div class="priority-chip priority-media">
          <span class="priority-dot"></span>
          <span>Média</span>
          <strong>{{ countByPriority('media') }}</strong>
        </div>
        <div class="priority-chip priority-baixa">
          <span class="priority-dot"></span>
          <span>Baixa</span>
          <strong>{{ countByPriority('baixa') }}</strong>
        </div>
      </div>

      <div class="rec-grid">
        <div v-for="r in filtered" :key="r.id" class="rec-card card">
          <div class="rec-card-header">
            <span :class="`badge badge-${r.prioridade}`">{{ priorityLabel(r.prioridade) }}</span>
            <span class="rec-date">{{ formatDate(r.criado_em) }}</span>
          </div>
          <div class="rec-tipo">{{ r.tipo }}</div>
          <div class="rec-desc">{{ r.descricao }}</div>
          <div class="rec-analysis">Análise #{{ r.analise_id }}</div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import AppLayout from '@/components/AppLayout.vue'
import api from '@/services/api'
import type { Recommendation, Property } from '@/types'

const recommendations = ref<Recommendation[]>([])
const properties = ref<Property[]>([])
const loading = ref(true)
const error = ref('')
const filterPropId = ref<number | ''>('')
const filterPriority = ref('')

const filtered = computed(() => {
  if (!filterPriority.value) return recommendations.value
  return recommendations.value.filter(x => x.prioridade === filterPriority.value)
})

function countByPriority(p: string) {
  return recommendations.value.filter(r => r.prioridade === p).length
}
function priorityLabel(p: string) {
  return { alta: 'Alta', media: 'Média', baixa: 'Baixa' }[p] ?? p
}
function formatDate(d: string) {
  return new Date(d).toLocaleDateString('pt-BR')
}
function clearFilters() {
  filterPropId.value = ''
  filterPriority.value = ''
}

async function fetchRecommendations() {
  loading.value = true
  error.value = ''
  try {
    const params: Record<string, unknown> = {}
    if (filterPropId.value) params.propriedade_id = filterPropId.value
    const { data } = await api.get('/api/recommendations/', { params })
    recommendations.value = data
  } catch {
    error.value = 'Erro ao carregar recomendações'
  } finally {
    loading.value = false
  }
}

watch(filterPropId, fetchRecommendations)

onMounted(async () => {
  const [, propsRes] = await Promise.allSettled([
    fetchRecommendations(),
    api.get('/api/properties/'),
  ])
  if (propsRes.status === 'fulfilled') {
    properties.value = propsRes.value.data
  }
})
</script>

<style scoped>
.empty-state-icon svg { width: 40px; height: 40px; }
.filters-card { margin-bottom: 20px; }
.filters-row { display: flex; gap: 12px; align-items: flex-start; flex-wrap: wrap; }

.priority-summary { display: flex; gap: 12px; margin-bottom: 20px; flex-wrap: wrap; }
.priority-chip {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 99px;
  font-size: 13px;
}
.priority-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}
.priority-alta { background: #fce4e4; color: #c1121f; }
.priority-alta .priority-dot { background: #c1121f; }
.priority-media { background: #fef3e2; color: #c07000; }
.priority-media .priority-dot { background: #c07000; }
.priority-baixa { background: #e8f5ee; color: #2d6a4f; }
.priority-baixa .priority-dot { background: #2d6a4f; }
.priority-chip strong { font-size: 16px; }

.rec-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 16px; }
.rec-card { padding: 18px; }
.rec-card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.rec-date { font-size: 12px; color: var(--color-text-muted); }
.rec-tipo { font-size: 15px; font-weight: 700; color: var(--color-text); margin-bottom: 8px; }
.rec-desc { font-size: 13px; color: var(--color-text-muted); line-height: 1.6; margin-bottom: 10px; }
.rec-analysis { font-size: 11px; color: var(--color-text-muted); font-style: italic; }
</style>
