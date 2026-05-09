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
          <div class="stat-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="18" height="18">
              <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
              <polyline points="9 22 9 12 15 12 15 22"/>
            </svg>
          </div>
          <div class="stat-label">Propriedades</div>
          <div class="stat-value">{{ stats.properties }}</div>
          <div class="stat-hint">cadastradas</div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="18" height="18">
              <path d="M9 3H5a2 2 0 0 0-2 2v4m6-6h10a2 2 0 0 1 2 2v4M9 3v11m0 0l3 3m-3-3l-3 3m12-14v11m0 0l3 3m-3-3l-3 3"/>
            </svg>
          </div>
          <div class="stat-label">Análises</div>
          <div class="stat-value">{{ stats.analyses }}</div>
          <div class="stat-hint">realizadas</div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="18" height="18">
              <circle cx="12" cy="12" r="10"/>
              <line x1="12" y1="8" x2="12" y2="12"/>
              <line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
          </div>
          <div class="stat-label">Recomendações</div>
          <div class="stat-value">{{ stats.recommendations }}</div>
          <div class="stat-hint">geradas</div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" :class="{ 'stat-icon--danger': stats.critical > 0 }">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="18" height="18">
              <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
              <line x1="12" y1="9" x2="12" y2="13"/>
              <line x1="12" y1="17" x2="12.01" y2="17"/>
            </svg>
          </div>
          <div class="stat-label">Alertas Críticos</div>
          <div class="stat-value" :style="{ color: stats.critical > 0 ? 'var(--color-danger)' : 'var(--color-text)' }">
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
                <div class="score-row">
                  <div class="score-bar-wrap">
                    <div
                      class="score-bar"
                      :style="{
                        width: calcularScore(a) + '%',
                        background: scoreColor(calcularScore(a))
                      }"
                    />
                  </div>
                  <span class="score-label" :style="{ color: scoreColor(calcularScore(a)) }">
                    {{ calcularScore(a) }} — {{ scoreLabel(calcularScore(a)) }}
                  </span>
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
                <span :class="`badge badge-${r.prioridade}`">{{ priorityLabel(r.prioridade) }}</span>
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
import { calcularScore, scoreColor, scoreLabel } from '@/composables/soilMetrics'

const loading = ref(true)
const stats = ref({ properties: 0, analyses: 0, recommendations: 0, critical: 0 })
const recentAnalyses = ref<SoilAnalysis[]>([])
const recentRecs = ref<Recommendation[]>([])

function formatDate(d: string) {
  return new Date(d).toLocaleDateString('pt-BR')
}

function priorityLabel(p: string) {
  return ({ alta: 'Alta', media: 'Média', baixa: 'Baixa' } as Record<string, string>)[p] ?? p
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

/* Stat icon */
.stat-icon {
  width: 36px;
  height: 36px;
  border-radius: var(--radius);
  background: var(--color-primary-light);
  color: var(--color-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 14px;
  flex-shrink: 0;
}
.stat-icon--danger {
  background: var(--color-danger-bg);
  color: var(--color-danger);
}

/* Analysis list */
.analysis-list { display: flex; flex-direction: column; gap: 8px; margin-bottom: 12px; }
.analysis-item {
  padding: 10px 12px;
  background: var(--color-surface-2);
  border-radius: var(--radius);
  border: 1px solid var(--color-border);
}
.analysis-main { display: flex; justify-content: space-between; margin-bottom: 3px; }
.analysis-id { font-weight: 600; font-size: 13px; }
.analysis-date { font-size: 12px; color: var(--color-text-muted); }
.analysis-sub { font-size: 12px; color: var(--color-text-muted); margin-bottom: 8px; }

.score-row { display: flex; align-items: center; gap: 8px; }
.score-bar-wrap {
  flex: 1;
  height: 5px;
  background: var(--color-border);
  border-radius: 99px;
  overflow: hidden;
}
.score-bar {
  height: 100%;
  border-radius: 99px;
  transition: width 0.6s ease;
}
.score-label { font-size: 11px; font-weight: 600; white-space: nowrap; }

/* Rec list */
.rec-list { display: flex; flex-direction: column; gap: 6px; margin-bottom: 12px; }
.rec-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: var(--color-surface-2);
  border-radius: var(--radius);
  border: 1px solid var(--color-border);
}
.rec-tipo { font-size: 13px; font-weight: 500; }

.card-link { font-size: 13px; color: var(--color-primary); font-weight: 500; display: block; margin-top: 10px; }
</style>
