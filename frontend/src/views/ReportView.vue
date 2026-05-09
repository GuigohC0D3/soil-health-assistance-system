<template>
  <AppLayout>
    <div class="page-header">
      <div>
        <h2 class="page-title">Relatórios</h2>
        <p class="page-subtitle">Visão consolidada por propriedade</p>
      </div>
      <button class="btn btn-primary" @click="exportPDF" :disabled="!selectedPropId || exporting">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="15" height="15">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
          <polyline points="7 10 12 15 17 10"/>
          <line x1="12" y1="15" x2="12" y2="3"/>
        </svg>
        {{ exporting ? 'Gerando PDF...' : 'Exportar PDF' }}
      </button>
    </div>

    <div class="card" style="margin-bottom: 24px;">
      <div class="card-body" style="padding: 14px 20px;">
        <div class="form-group" style="margin:0; max-width: 320px;">
          <label class="form-label">Selecione a Propriedade</label>
          <select v-model="selectedPropId" class="form-control">
            <option value="">Selecione...</option>
            <option v-for="p in properties" :key="p.id" :value="p.id">{{ p.nome }}</option>
          </select>
        </div>
      </div>
    </div>

    <div v-if="!selectedPropId" class="empty-state">
      <div class="empty-state-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
          <polyline points="14 2 14 8 20 8"/>
          <line x1="16" y1="13" x2="8" y2="13"/>
          <line x1="16" y1="17" x2="8" y2="17"/>
          <polyline points="10 9 9 9 8 9"/>
        </svg>
      </div>
      <div class="empty-state-title">Selecione uma propriedade</div>
      <div class="empty-state-desc">Escolha uma propriedade para visualizar o relatório.</div>
    </div>

    <template v-else-if="selectedProp">
      <div id="report-area">
        <div class="report-header card">
          <div class="card-body">
            <h2 class="report-prop-name">{{ selectedProp.nome }}</h2>
            <div class="report-meta">
              <span v-if="selectedProp.cidade || selectedProp.estado" class="meta-item">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="13" height="13"><path d="M21 10c0 7-9 13-9 13S3 17 3 10a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
                {{ [selectedProp.cidade, selectedProp.estado].filter(Boolean).join(' - ') }}
              </span>
              <span v-if="selectedProp.area_hectares" class="meta-item">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="13" height="13"><polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21"/><line x1="9" y1="3" x2="9" y2="18"/><line x1="15" y1="6" x2="15" y2="21"/></svg>
                {{ selectedProp.area_hectares.toLocaleString('pt-BR') }} hectares
              </span>
              <span class="meta-item">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="13" height="13"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
                Gerado em {{ today }}
              </span>
            </div>
          </div>
        </div>

        <div class="grid-4" style="margin: 20px 0;">
          <div class="stat-card">
            <div class="stat-label">Análises Realizadas</div>
            <div class="stat-value">{{ propAnalyses.length }}</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">Última Análise</div>
            <div class="stat-value" style="font-size: 16px;">{{ lastAnalysisDate }}</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">Recomendações</div>
            <div class="stat-value">{{ totalRecs }}</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">Score Atual</div>
            <div class="stat-value" :style="{ color: latestScore !== null ? scoreColor(latestScore) : 'var(--color-primary)', fontSize: '28px' }">
              {{ latestScore !== null ? latestScore : '—' }}
            </div>
            <div class="stat-hint" v-if="latestScore !== null">{{ scoreLabel(latestScore) }}</div>
          </div>
        </div>

        <!-- Gráficos -->
        <div class="grid-2" style="margin-bottom: 20px;">
          <div class="card">
            <div class="card-header">Perfil de Adequação do Solo</div>
            <div class="card-body" v-if="latestAnalysis">
              <SoilRadarChart :analysis="latestAnalysis" />
              <p class="chart-hint">Baseado na última análise: {{ formatDate(latestAnalysis.data_analise) }}</p>
            </div>
            <div class="card-body" v-else>
              <p class="no-data">Nenhuma análise registrada para esta propriedade.</p>
            </div>
          </div>
          <div class="card">
            <div class="card-header">Evolução da Saúde do Solo</div>
            <div class="card-body">
              <HealthEvolutionChart :analyses="propAnalyses" />
            </div>
          </div>
        </div>

        <div class="card" style="margin-bottom: 20px;">
          <div class="card-header">Histórico de Análises</div>
          <div v-if="propAnalyses.length === 0" class="card-body">
            <p style="color: var(--color-text-muted); font-size: 13px;">Nenhuma análise registrada para esta propriedade.</p>
          </div>
          <div v-else class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Amostra</th><th>Data</th><th>pH</th><th>M.O. (%)</th>
                  <th>P (mg/dm³)</th><th>K (cmolc)</th><th>Ca (cmolc)</th><th>Mg (cmolc)</th><th>Score</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="a in propAnalyses" :key="a.id">
                  <td>{{ a.id_amostra }}</td>
                  <td>{{ formatDate(a.data_analise) }}</td>
                  <td :class="phClass(a.ph)">{{ a.ph ?? '—' }}</td>
                  <td :class="moClass(a.materia_organica)">{{ a.materia_organica ?? '—' }}</td>
                  <td :class="pClass(a.fosforo)">{{ a.fosforo ?? '—' }}</td>
                  <td :class="kClass(a.potassio)">{{ a.potassio ?? '—' }}</td>
                  <td>{{ a.calcio ?? '—' }}</td>
                  <td>{{ a.magnesio ?? '—' }}</td>
                  <td>
                    <span class="score-chip" :style="{ background: scoreColor(calcularScore(a)) + '20', color: scoreColor(calcularScore(a)) }">
                      {{ calcularScore(a) }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="card">
          <div class="card-header">Recomendações de Manejo</div>
          <div v-if="propRecs.length === 0" class="card-body">
            <p style="color: var(--color-text-muted); font-size: 13px;">Nenhuma recomendação disponível.</p>
          </div>
          <div v-else class="card-body rec-list">
            <div v-for="r in propRecs" :key="r.id" class="rec-row">
              <span :class="`badge badge-${r.prioridade}`">{{ priorityLabel(r.prioridade) }}</span>
              <div class="rec-content">
                <div class="rec-tipo">{{ r.tipo }}</div>
                <div class="rec-desc">{{ r.descricao }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import AppLayout from '@/components/AppLayout.vue'
import SoilRadarChart from '@/components/SoilRadarChart.vue'
import HealthEvolutionChart from '@/components/HealthEvolutionChart.vue'
import api from '@/services/api'
import type { Property, SoilAnalysis, Recommendation } from '@/types'
import { calcularScore, scoreColor, scoreLabel } from '@/composables/soilMetrics'

const properties = ref<Property[]>([])
const selectedPropId = ref<number | ''>('')
const propAnalyses = ref<SoilAnalysis[]>([])
const propRecs = ref<Recommendation[]>([])
const exporting = ref(false)

const selectedProp = computed(() => properties.value.find(p => p.id === selectedPropId.value))
const today = new Date().toLocaleDateString('pt-BR')
const latestAnalysis = computed(() => propAnalyses.value.length ? propAnalyses.value[0] : null)
const latestScore = computed(() => latestAnalysis.value ? calcularScore(latestAnalysis.value) : null)
const lastAnalysisDate = computed(() => propAnalyses.value.length ? formatDate(propAnalyses.value[0].data_analise) : '—')
const totalRecs = computed(() => propRecs.value.length)

function formatDate(d: string) { return new Date(d).toLocaleDateString('pt-BR') }
function priorityLabel(p: string) { return ({ alta: 'Alta', media: 'Média', baixa: 'Baixa' } as Record<string, string>)[p] ?? p }
function phClass(v: number | null) { if (v === null || v === undefined) return ''; return v < 5.5 ? 'val-low' : v > 7.5 ? 'val-warn' : 'val-ok' }
function moClass(v: number | null) { if (v === null || v === undefined) return ''; return v < 2.5 ? 'val-low' : 'val-ok' }
function pClass(v: number | null) { if (v === null || v === undefined) return ''; return v < 10 ? 'val-low' : 'val-ok' }
function kClass(v: number | null) { if (v === null || v === undefined) return ''; return v < 0.15 ? 'val-low' : 'val-ok' }

async function exportPDF() {
  if (!selectedPropId.value) return
  exporting.value = true
  try {
    const [{ default: html2canvas }, { default: jsPDF }] = await Promise.all([
      import('html2canvas'),
      import('jspdf'),
    ])
    const el = document.getElementById('report-area')!
    const canvas = await html2canvas(el, { scale: 2, useCORS: true, backgroundColor: '#ffffff' })
    const imgData = canvas.toDataURL('image/png')
    const pdf = new jsPDF({ orientation: 'p', unit: 'mm', format: 'a4' })
    const pageW = pdf.internal.pageSize.getWidth()
    const pageH = pdf.internal.pageSize.getHeight()
    const imgH = (canvas.height * pageW) / canvas.width
    let heightLeft = imgH
    let position = 0
    pdf.addImage(imgData, 'PNG', 0, position, pageW, imgH)
    heightLeft -= pageH
    while (heightLeft > 0) {
      position -= pageH
      pdf.addPage()
      pdf.addImage(imgData, 'PNG', 0, position, pageW, imgH)
      heightLeft -= pageH
    }
    pdf.save(`relatorio-${selectedProp.value?.nome ?? 'solo'}.pdf`)
  } finally {
    exporting.value = false
  }
}

watch(selectedPropId, async (id) => {
  if (!id) { propAnalyses.value = []; propRecs.value = []; return }
  const [aRes, rRes] = await Promise.all([
    api.get('/api/analyses/', { params: { propriedade_id: id } }),
    api.get('/api/recommendations/', { params: { propriedade_id: id } }),
  ])
  propAnalyses.value = aRes.data
  propRecs.value = rRes.data
})

onMounted(async () => {
  const { data } = await api.get('/api/properties/')
  properties.value = data
})
</script>

<style scoped>
.empty-state-icon svg { width: 40px; height: 40px; }
.report-prop-name { font-size: 20px; font-weight: 700; margin-bottom: 10px; }
.report-meta { display: flex; gap: 16px; flex-wrap: wrap; }
.meta-item { display: flex; align-items: center; gap: 5px; font-size: 13px; color: var(--color-text-muted); }

.rec-list { display: flex; flex-direction: column; gap: 14px; }
.rec-row { display: flex; gap: 12px; align-items: flex-start; }
.rec-content { flex: 1; }
.rec-tipo { font-weight: 600; font-size: 14px; margin-bottom: 3px; }
.rec-desc { font-size: 13px; color: var(--color-text-muted); line-height: 1.6; }

.val-low { color: var(--color-danger); font-weight: 600; }
.val-warn { color: var(--color-warning); font-weight: 600; }
.val-ok { color: var(--color-success); }

.score-chip {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 99px;
  font-size: 12px;
  font-weight: 700;
}

.chart-hint {
  text-align: center;
  font-size: 12px;
  color: var(--color-text-muted);
  margin-top: 10px;
}
.no-data {
  color: var(--color-text-muted);
  font-size: 13px;
}

@media print {
  .page-header .btn { display: none !important; }
}
</style>
