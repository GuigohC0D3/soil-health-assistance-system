<template>
  <AppLayout>
    <div class="page-header">
      <div>
        <h2 class="page-title">Simulador de Calagem</h2>
        <p class="page-subtitle">Simule o efeito da aplicação de calcário na saturação de bases e pH do solo</p>
      </div>
    </div>

    <div class="card" style="margin-bottom:20px;">
      <div class="card-body" style="padding:14px 20px;">
        <div class="filters-row">
          <div class="form-group" style="margin:0;min-width:220px;">
            <label class="form-label">Propriedade</label>
            <select v-model="selectedPropId" class="form-control" @change="onPropChange">
              <option value="">Selecione a propriedade...</option>
              <option v-for="p in properties" :key="p.id" :value="p.id">{{ p.nome }}</option>
            </select>
          </div>
          <div v-if="selectedPropId" class="form-group" style="margin:0;min-width:260px;">
            <label class="form-label">Análise de Solo</label>
            <select v-model="selectedAnalysisId" class="form-control" @change="onAnalysisChange">
              <option value="">Selecione a análise...</option>
              <option v-for="a in propAnalyses" :key="a.id" :value="a.id">
                {{ a.id_amostra }} — {{ formatDate(a.data_analise) }}
              </option>
            </select>
          </div>
          <div v-if="selectedAnalysisId" class="form-group" style="margin:0;min-width:180px;">
            <label class="form-label">Cultura</label>
            <select v-model="cultura" class="form-control" @change="onCulturaChange">
              <option value="">Selecione...</option>
              <option v-for="c in culturas" :key="c" :value="c">{{ c }}</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <div v-if="error" class="alert alert-error" style="margin-bottom:16px;">{{ error }}</div>

    <template v-if="selectedAnalysisId && cultura">
      <div class="slider-card card" style="margin-bottom:20px;">
        <div class="card-body">
          <div class="slider-header">
            <span class="slider-label">Dosagem de Calcário</span>
            <span class="slider-value">{{ dosagem.toFixed(1) }} t/ha</span>
          </div>
          <input
            type="range"
            class="range-slider"
            min="0"
            max="5"
            step="0.1"
            v-model.number="dosagem"
          />
          <div class="slider-range">
            <span>0 t/ha</span>
            <span>5 t/ha</span>
          </div>
        </div>
      </div>

      <div v-if="loading" class="loading-state">
        <div class="spinner" />
        <span>Simulando...</span>
      </div>

      <div v-else-if="result" class="cards-grid">
        <div class="card status-card">
          <div class="card-header">
            <span class="card-header-icon">📊</span>
            Situação Atual
          </div>
          <div class="card-body">
            <div class="metric-row">
              <span class="metric-label">Saturação de bases (V%)</span>
              <span class="metric-value">{{ result.antes.v_pct }}%</span>
            </div>
            <div class="metric-row">
              <span class="metric-label">pH estimado</span>
              <span class="metric-value">{{ result.antes.ph_estimado }}</span>
            </div>
            <div class="metric-row">
              <span class="metric-label">Necessidade de calagem (NC)</span>
              <span class="metric-value" :class="ncClass(result.antes.necessidade_calagem)">
                {{ result.antes.necessidade_calagem ?? '—' }} t/ha
              </span>
            </div>
            <div class="metric-row">
              <span class="metric-label">Score de saúde do solo</span>
              <span class="metric-value">{{ result.antes.score_saude }}</span>
            </div>
          </div>
        </div>

        <div class="card status-card">
          <div class="card-header">
            <span class="card-header-icon">🔄</span>
            Após Aplicação
          </div>
          <div class="card-body">
            <div class="metric-row">
              <span class="metric-label">Saturação de bases (V%)</span>
              <span class="metric-value delta-positive" :class="{ 'delta-negative': vDelta < 0 }">
                {{ result.depois.v_pct_simulado }}%
                <span class="delta-badge" :class="vDelta >= 0 ? 'delta-up' : 'delta-down'">
                  {{ vDelta >= 0 ? '+' : '' }}{{ vDelta.toFixed(1) }}
                </span>
              </span>
            </div>
            <div class="metric-row">
              <span class="metric-label">pH estimado</span>
              <span class="metric-value delta-positive" :class="{ 'delta-negative': phDelta < 0 }">
                {{ result.depois.ph_simulado }}
                <span class="delta-badge" :class="phDelta >= 0 ? 'delta-up' : 'delta-down'">
                  {{ phDelta >= 0 ? '+' : '' }}{{ phDelta.toFixed(1) }}
                </span>
              </span>
            </div>
          </div>
        </div>
      </div>

      <div v-if="result && result.narrativa" class="narrativa-card card">
        <div class="card-body narrativa-body">
          <span class="narrativa-icon">💬</span>
          <p class="narrativa-text">{{ result.narrativa }}</p>
        </div>
      </div>
    </template>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import AppLayout from '@/components/AppLayout.vue'
import api from '@/services/api'
import type { Property, SoilAnalysis } from '@/types'

interface LimingAntes {
  v_pct: number
  ph_estimado: number
  necessidade_calagem: number | null
  score_saude: number
}

interface LimingDepois {
  v_pct_simulado: number
  ph_simulado: number
}

interface LimingSimulation {
  antes: LimingAntes
  depois: LimingDepois
  narrativa: string
}

const properties = ref<Property[]>([])
const propAnalyses = ref<SoilAnalysis[]>([])
const selectedPropId = ref<number | ''>('')
const selectedAnalysisId = ref<number | ''>('')
const cultura = ref('')
const dosagem = ref(0)
const result = ref<LimingSimulation | null>(null)
const loading = ref(false)
const error = ref('')

const culturas = ['Soja', 'Milho', 'Feijão', 'Sorgo', 'Pastagem']

let debounceTimer: ReturnType<typeof setTimeout> | null = null

const vDelta = ref(0)
const phDelta = ref(0)

function formatDate(d: string) {
  return new Date(d).toLocaleDateString('pt-BR')
}

function ncClass(v: number | null) {
  if (v === null) return ''
  return v > 0 ? 'metric-warning' : 'metric-ok'
}

async function onPropChange() {
  propAnalyses.value = []
  selectedAnalysisId.value = ''
  cultura.value = ''
  result.value = null
  dosagem.value = 0
  if (!selectedPropId.value) return
  const { data } = await api.get('/api/analyses/', { params: { propriedade_id: selectedPropId.value } })
  propAnalyses.value = data
}

function onAnalysisChange() {
  result.value = null
  dosagem.value = 0
}

function onCulturaChange() {
  result.value = null
  dosagem.value = 0
  if (selectedAnalysisId.value && cultura.value) simulate()
}

async function simulate() {
  if (!selectedAnalysisId.value || !cultura.value) return

  loading.value = true
  error.value = ''
  try {
    const { data } = await api.post<LimingSimulation>('/api/simulate/liming', {
      analise_id: selectedAnalysisId.value,
      dosagem_calcario: dosagem.value,
      cultura: cultura.value,
    })
    result.value = data
    vDelta.value = data.depois.v_pct_simulado - data.antes.v_pct
    phDelta.value = data.depois.ph_simulado - data.antes.ph_estimado
  } catch (e: unknown) {
    const err = e as { response?: { data?: { detail?: string } } }
    error.value = err?.response?.data?.detail ?? 'Erro ao simular calagem.'
  } finally {
    loading.value = false
  }
}

watch(dosagem, () => {
  if (!selectedAnalysisId.value || !cultura.value) return
  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = setTimeout(async () => {
    if (!loading.value) await simulate()
  }, 400)
})

onMounted(async () => {
  try {
    const { data } = await api.get('/api/properties/')
    properties.value = data
  } catch {
    // silêncio
  }
})
</script>

<style scoped>
.filters-row { display: flex; gap: 12px; align-items: flex-start; flex-wrap: wrap; }

.slider-card { }
.slider-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}
.slider-label { font-weight: 600; font-size: 14px; }
.slider-value {
  font-size: 18px;
  font-weight: 700;
  color: var(--color-primary);
}

.range-slider {
  -webkit-appearance: none;
  appearance: none;
  width: 100%;
  height: 6px;
  border-radius: 3px;
  background: var(--color-border);
  outline: none;
  cursor: pointer;
}
.range-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: var(--color-primary);
  cursor: pointer;
  border: 3px solid var(--color-surface);
  box-shadow: 0 1px 4px rgba(0,0,0,0.15);
  transition: transform 0.1s;
}
.range-slider::-webkit-slider-thumb:hover { transform: scale(1.15); }
.range-slider::-moz-range-thumb {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: var(--color-primary);
  cursor: pointer;
  border: 3px solid var(--color-surface);
  box-shadow: 0 1px 4px rgba(0,0,0,0.15);
}
.slider-range {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: var(--color-text-muted);
  margin-top: 6px;
}

.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 32px;
  color: var(--color-text-muted);
  font-size: 14px;
}
.spinner {
  width: 20px;
  height: 20px;
  border: 2.5px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.cards-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 16px;
}
@media (max-width: 768px) { .cards-grid { grid-template-columns: 1fr; } }

.status-card { }
.metric-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 9px 0;
  border-bottom: 1px solid var(--color-border);
  font-size: 13px;
}
.metric-row:last-child { border-bottom: none; }
.metric-label { color: var(--color-text-muted); }
.metric-value { font-weight: 600; display: flex; align-items: center; gap: 8px; }
.metric-warning { color: var(--color-danger); }
.metric-ok { color: var(--color-primary); }

.delta-positive { color: var(--color-primary); }
.delta-negative { color: var(--color-danger); }

.delta-badge {
  display: inline-flex;
  align-items: center;
  font-size: 11px;
  font-weight: 700;
  padding: 2px 7px;
  border-radius: 99px;
}
.delta-up {
  background: var(--color-success-bg);
  color: var(--color-primary);
}
.delta-down {
  background: var(--color-danger-bg);
  color: var(--color-danger);
}

.narrativa-card {
  border-left: 3px solid var(--color-primary);
  animation: fadeSlideIn 0.5s ease;
}
@keyframes fadeSlideIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}
.narrativa-body {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}
.narrativa-icon { font-size: 20px; flex-shrink: 0; margin-top: 1px; }
.narrativa-text {
  font-style: italic;
  font-size: 13.5px;
  line-height: 1.7;
  color: var(--color-text);
  margin: 0;
}
</style>
