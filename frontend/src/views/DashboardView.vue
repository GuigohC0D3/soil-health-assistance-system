<template>
  <AppLayout>
    <div class="page-header">
      <div>
        <h2 class="page-title">Dashboard</h2>
        <p class="page-subtitle">Visão geral do sistema</p>
      </div>
    </div>

    <div v-if="loading" class="loading-text">Carregando...</div>

    <template v-else>
      <div class="grid-4" style="margin-bottom: 28px;">
        <div class="stat-card">
          <div class="stat-label">Propriedades</div>
          <div class="stat-value">{{ stats.properties }}</div>
          <div class="stat-hint">cadastradas</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Análises</div>
          <div class="stat-value">{{ stats.analyses }}</div>
          <div class="stat-hint">realizadas</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Recomendações</div>
          <div class="stat-value">{{ stats.recommendations }}</div>
          <div class="stat-hint">geradas</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Alertas Críticos</div>
          <div class="stat-value" :style="{ color: stats.critical > 0 ? 'var(--color-danger)' : 'var(--color-primary)' }">
            {{ stats.critical }}
          </div>
          <div class="stat-hint">prioridade alta</div>
        </div>
      </div>

      <div class="grid-2">
        <div class="card">
          <div class="card-header">Últimas Análises</div>
          <div class="card-body">
            <div v-if="recentAnalyses.length === 0" class="empty-state">
              <div class="empty-state-desc">Nenhuma análise registrada ainda.</div>
            </div>
            <div v-else class="analysis-list">
              <div v-for="a in recentAnalyses" :key="a.id" class="analysis-item">
                <div class="analysis-main">
                  <span class="analysis-id">{{ a.id_amostra }}</span>
                  <span class="analysis-date">{{ formatDate(a.data_analise) }}</span>
                </div>
                <div class="analysis-sub">
                  pH: {{ a.ph ?? '—' }} | MO: {{ a.materia_organica ?? '—' }}%
                </div>
              </div>
            </div>
            <RouterLink to="/analyses" class="card-link">Ver todas as análises</RouterLink>
          </div>
        </div>

        <div class="card">
          <div class="card-header">Recomendações Recentes</div>
          <div class="card-body">
            <div v-if="recentRecs.length === 0" class="empty-state">
              <div class="empty-state-desc">Nenhuma recomendação gerada ainda.</div>
            </div>
            <div v-else class="rec-list">
              <div v-for="r in recentRecs" :key="r.id" class="rec-item">
                <span :class="`badge badge-${r.prioridade}`">{{ r.prioridade }}</span>
                <span class="rec-tipo">{{ r.tipo }}</span>
              </div>
            </div>
            <RouterLink to="/recommendations" class="card-link">Ver todas</RouterLink>
          </div>
        </div>
      </div>
    </template>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import AppLayout from '@/components/AppLayout.vue'
import api from '@/services/api'
import type { SoilAnalysis, Recommendation } from '@/types'

const loading = ref(true)
const stats = ref({ properties: 0, analyses: 0, recommendations: 0, critical: 0 })
const recentAnalyses = ref<SoilAnalysis[]>([])
const recentRecs = ref<Recommendation[]>([])

function formatDate(d: string) {
  return new Date(d).toLocaleDateString('pt-BR')
}

onMounted(async () => {
  try {
    const [statsRes, analysesRes, recsRes] = await Promise.all([
      api.get('/api/dashboard/stats'),
      api.get('/api/analyses/', { params: { limit: 5 } }),
      api.get('/api/recommendations/', { params: { limit: 6 } }),
    ])
    stats.value = statsRes.data
    recentAnalyses.value = analysesRes.data
    recentRecs.value = recsRes.data
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.loading-text { color: var(--color-text-muted); padding: 24px 0; }

.analysis-list { display: flex; flex-direction: column; gap: 8px; margin-bottom: 12px; }
.analysis-item { padding: 10px 12px; background: #f8faf8; border-radius: 6px; border: 1px solid var(--color-border); }
.analysis-main { display: flex; justify-content: space-between; margin-bottom: 3px; }
.analysis-id { font-weight: 600; font-size: 13px; }
.analysis-date { font-size: 12px; color: var(--color-text-muted); }
.analysis-sub { font-size: 12px; color: var(--color-text-muted); }

.rec-list { display: flex; flex-direction: column; gap: 8px; margin-bottom: 12px; }
.rec-item { display: flex; align-items: center; gap: 8px; padding: 8px 12px; background: #f8faf8; border-radius: 6px; border: 1px solid var(--color-border); }
.rec-tipo { font-size: 13px; font-weight: 500; }

.card-link { font-size: 13px; color: var(--color-primary); font-weight: 500; display: block; margin-top: 8px; }
</style>
