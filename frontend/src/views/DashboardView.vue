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
      <!-- Stat cards -->
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

      <!-- Gauge + Ranking -->
      <div class="grid-2" style="margin-bottom: 24px;">
        <!-- Health Gauge -->
        <div class="card">
          <div class="card-header">Score de Saúde — Última Análise</div>
          <div class="card-body" style="display:flex;flex-direction:column;align-items:center;gap:10px;padding-top:20px;padding-bottom:20px;">
            <template v-if="recentAnalyses.length > 0">
              <SoilGaugeChart :score="calcularScore(recentAnalyses[0])" />
              <div style="font-size:12px;color:var(--color-text-muted);text-align:center;">
                Amostra: <strong>{{ recentAnalyses[0].id_amostra }}</strong> —
                {{ formatDate(recentAnalyses[0].data_analise) }}
              </div>
            </template>
            <div v-else style="color:var(--color-text-muted);font-size:13px;">
              Nenhuma análise registrada ainda.
            </div>
          </div>
        </div>

        <!-- Top 3 Ranking -->
        <div class="card">
          <div class="card-header">Top 3 Propriedades — Saúde do Solo</div>
          <div class="card-body">
            <div v-if="!trends || trends.top3_propriedades.length === 0" style="color:var(--color-text-muted);font-size:13px;">
              Cadastre propriedades com análises para ver o ranking.
            </div>
            <div v-else class="ranking-list">
              <div
                v-for="(p, idx) in trends.top3_propriedades"
                :key="p.propriedade_id"
                class="ranking-item"
                @click="router.push(`/analyses?propriedade_id=${p.propriedade_id}`)"
              >
                <span class="ranking-pos" :class="`pos-${idx + 1}`">#{{ idx + 1 }}</span>
                <div class="ranking-info">
                  <div class="ranking-name">{{ p.nome }}</div>
                  <div class="ranking-bar-wrap">
                    <div
                      class="ranking-bar"
                      :style="{ width: p.score + '%', background: scoreColor(p.score) }"
                    />
                  </div>
                </div>
                <span class="ranking-score" :style="{ color: scoreColor(p.score) }">{{ p.score }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- pH Trend Sparkline -->
      <div class="card" style="margin-bottom: 24px;" v-if="trends && trends.ph_trend.length >= 2">
        <div class="card-header" style="display:flex;justify-content:space-between;align-items:center;">
          <span>Tendência de pH — Propriedade Mais Recente</span>
          <RouterLink
            v-if="trends.ph_trend_prop_id"
            :to="`/analyses?propriedade_id=${trends.ph_trend_prop_id}`"
            style="font-size:12px;font-weight:400;color:var(--color-primary);"
          >Ver análises</RouterLink>
        </div>
        <div class="card-body">
          <div class="ph-trend-chart">
            <svg :viewBox="`0 0 ${SVG_W} 65`" class="sparkline-svg">
              <!-- Ideal band 5.5–6.5 -->
              <rect
                x="0" :y="phY(6.5)"
                :width="SVG_W" :height="phY(5.5) - phY(6.5)"
                fill="rgba(22,163,74,0.08)"
              />
              <text x="4" :y="phY(6.5) - 2" font-size="7" fill="#16a34a">Faixa ideal</text>
              <!-- Connecting line -->
              <polyline
                :points="phPoints"
                fill="none" stroke="#3b82f6" stroke-width="2"
                stroke-linecap="round" stroke-linejoin="round"
              />
              <!-- Data points -->
              <circle
                v-for="(pt, i) in phDataPoints" :key="i"
                :cx="pt.x" :cy="pt.y" r="4"
                :fill="pt.ph < 5.5 ? '#ef4444' : pt.ph > 6.5 ? '#f59e0b' : '#16a34a'"
                stroke="#fff" stroke-width="1.5"
              />
              <!-- Date labels -->
              <text
                v-for="(pt, i) in phDataPoints" :key="`l${i}`"
                :x="pt.x" :y="62"
                text-anchor="middle" font-size="7" fill="#64748b"
              >{{ pt.label }}</text>
              <!-- pH value labels -->
              <text
                v-for="(pt, i) in phDataPoints" :key="`v${i}`"
                :x="pt.x" :y="pt.y - 7"
                text-anchor="middle" font-size="7" font-weight="600"
                :fill="pt.ph < 5.5 ? '#ef4444' : pt.ph > 6.5 ? '#f59e0b' : '#16a34a'"
              >{{ pt.ph }}</text>
            </svg>
          </div>
          <div class="sparkline-legend">
            <span class="legend-dot" style="background:#16a34a;"></span> pH ideal (5.5–6.5)
            <span class="legend-dot" style="background:#ef4444;margin-left:12px;"></span> Ácido
            <span class="legend-dot" style="background:#f59e0b;margin-left:12px;"></span> Alcalino
          </div>
        </div>
      </div>

      <!-- Recent analyses + Recommendations -->
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
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import SoilGaugeChart from '@/components/SoilGaugeChart.vue'
import api from '@/services/api'
import type { SoilAnalysis, Recommendation } from '@/types'
import { calcularScore, scoreColor, scoreLabel } from '@/composables/soilMetrics'

const router = useRouter()
const loading = ref(true)
const stats = ref({ properties: 0, analyses: 0, recommendations: 0, critical: 0 })
const recentAnalyses = ref<SoilAnalysis[]>([])
const recentRecs = ref<Recommendation[]>([])

interface TrendData {
  top3_propriedades: Array<{ propriedade_id: number; nome: string; score: number; ultima_analise: string }>
  ph_trend: Array<{ data: string; ph: number; id_amostra: string }>
  ph_trend_prop_id: number | null
}
const trends = ref<TrendData | null>(null)

const SVG_W = 460
const PH_MIN = 4.0
const PH_MAX = 8.0

function phY(ph: number): number {
  return 5 + ((PH_MAX - ph) / (PH_MAX - PH_MIN)) * 48
}

const phDataPoints = computed(() => {
  if (!trends.value || trends.value.ph_trend.length === 0) return []
  const pts = trends.value.ph_trend
  return pts.map((pt, i) => ({
    x: pts.length === 1 ? SVG_W / 2 : (i / (pts.length - 1)) * (SVG_W - 60) + 30,
    y: phY(pt.ph),
    ph: pt.ph,
    label: new Date(pt.data).toLocaleDateString('pt-BR', { month: '2-digit', year: '2-digit' }),
  }))
})

const phPoints = computed(() =>
  phDataPoints.value.map(pt => `${pt.x},${pt.y}`).join(' ')
)

function formatDate(d: string) {
  return new Date(d).toLocaleDateString('pt-BR')
}

function priorityLabel(p: string) {
  return ({ alta: 'Alta', media: 'Média', baixa: 'Baixa' } as Record<string, string>)[p] ?? p
}

onMounted(async () => {
  try {
    const [statsRes, analysesRes, recsRes, trendsRes] = await Promise.all([
      api.get('/api/dashboard/stats'),
      api.get('/api/analyses/', { params: { limit: 5 } }),
      api.get('/api/recommendations/', { params: { limit: 6 } }),
      api.get('/api/dashboard/trends'),
    ])
    stats.value = statsRes.data
    recentAnalyses.value = analysesRes.data
    recentRecs.value = recsRes.data
    trends.value = trendsRes.data
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.loading-text { color: var(--color-text-muted); padding: 24px 0; }

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

/* Ranking */
.ranking-list { display: flex; flex-direction: column; gap: 10px; }
.ranking-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: var(--radius);
  background: var(--color-surface-2);
  cursor: pointer;
  transition: background 0.1s;
}
.ranking-item:hover { background: var(--color-primary-light); }
.ranking-pos { font-size: 15px; font-weight: 800; width: 28px; text-align: center; flex-shrink: 0; }
.pos-1 { color: #f59e0b; }
.pos-2 { color: #94a3b8; }
.pos-3 { color: #b45309; }
.ranking-info { flex: 1; min-width: 0; }
.ranking-name { font-size: 13px; font-weight: 600; margin-bottom: 5px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.ranking-bar-wrap { height: 5px; background: var(--color-border); border-radius: 99px; overflow: hidden; }
.ranking-bar { height: 100%; border-radius: 99px; transition: width 0.6s ease; }
.ranking-score { font-size: 16px; font-weight: 700; flex-shrink: 0; }

/* pH Sparkline */
.ph-trend-chart { overflow-x: auto; }
.sparkline-svg { width: 100%; height: 70px; display: block; }
.sparkline-legend { font-size: 11px; color: var(--color-text-muted); margin-top: 6px; display: flex; align-items: center; gap: 4px; flex-wrap: wrap; }
.legend-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; }

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
