<template>
  <AppLayout>
    <div class="page-header">
      <div>
        <h2 class="page-title">Histórico de Análises</h2>
        <p class="page-subtitle">Todas as análises de solo registradas</p>
      </div>
      <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap;">
        <button
          class="btn btn-secondary"
          :disabled="selectedForComparison.length !== 2"
          @click="showComparison = true"
        >
          Comparar ({{ selectedForComparison.length }}/2)
        </button>
        <button class="btn btn-secondary" @click="exportCSV" :disabled="exporting">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15" style="margin-right:4px;">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
            <polyline points="7 10 12 15 17 10"/>
            <line x1="12" y1="15" x2="12" y2="3"/>
          </svg>
          {{ exporting ? 'Baixando...' : 'Baixar Planilha' }}
        </button>
        <RouterLink to="/analyses/new" class="btn btn-primary">+ Nova Análise</RouterLink>
      </div>
    </div>

    <div class="filters card" style="margin-bottom: 20px;">
      <div class="card-body" style="padding: 14px 20px;">
        <div class="filters-row">
          <div class="form-group" style="margin:0; min-width: 200px;">
            <label class="form-label">Propriedade</label>
            <select v-model="filterPropId" class="form-control">
              <option value="">Todas as propriedades</option>
              <option v-for="p in properties" :key="p.id" :value="p.id">{{ p.nome }}</option>
            </select>
          </div>
          <button class="btn btn-secondary" style="align-self: flex-end;" @click="filterPropId = ''; selectedForComparison = []">Limpar</button>
        </div>
      </div>
    </div>

    <div v-if="error" class="alert alert-error">{{ error }}</div>

    <div v-if="loading" class="empty-state"><div class="empty-state-desc">Carregando...</div></div>

    <div v-else-if="filtered.length === 0" class="empty-state">
      <div class="empty-state-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M9 3H5a2 2 0 0 0-2 2v4m6-6h10a2 2 0 0 1 2 2v4M9 3v11m0 0l3 3m-3-3l-3 3m12-14v11m0 0l3 3m-3-3l-3 3"/>
        </svg>
      </div>
      <div class="empty-state-title">Nenhuma análise encontrada</div>
      <div class="empty-state-desc">Registre a primeira análise de solo para uma propriedade.</div>
    </div>

    <div v-else class="card">
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th style="width:36px;"></th>
              <th>Amostra</th>
              <th>Propriedade</th>
              <th>Data</th>
              <th>pH</th>
              <th>M.O. (%)</th>
              <th>P (mg/dm³)</th>
              <th>K (cmolc)</th>
              <th>Score</th>
              <th>Recs.</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="a in filtered" :key="a.id" :class="{ 'row-selected': selectedForComparison.includes(a.id) }">
              <td>
                <input
                  type="checkbox"
                  :checked="selectedForComparison.includes(a.id)"
                  :disabled="!selectedForComparison.includes(a.id) && selectedForComparison.length >= 2"
                  @change="toggleComparison(a.id)"
                  style="cursor:pointer;width:16px;height:16px;"
                />
              </td>
              <td><strong>{{ a.id_amostra }}</strong></td>
              <td>{{ propName(a.propriedade_id) }}</td>
              <td>{{ formatDate(a.data_analise) }}</td>
              <td><span :class="phClass(a.ph)">{{ a.ph ?? '—' }}</span></td>
              <td>{{ a.materia_organica ?? '—' }}</td>
              <td>{{ a.fosforo ?? '—' }}</td>
              <td>{{ a.potassio ?? '—' }}</td>
              <td>
                <div class="score-cell">
                  <span class="score-chip" :style="{ background: scoreColor(calcularScore(a)) + '20', color: scoreColor(calcularScore(a)) }">
                    {{ calcularScore(a) }}
                  </span>
                  <span class="score-word" :style="{ color: scoreColor(calcularScore(a)) }">{{ scoreLabel(calcularScore(a)) }}</span>
                </div>
              </td>
              <td>
                <span class="badge" :class="recBadgeClass(a.recomendacoes)">
                  {{ a.recomendacoes.length }}
                </span>
              </td>
              <td>
                <div class="row-actions">
                  <RouterLink :to="`/analyses/${a.id}/edit`" class="btn btn-ghost btn-sm">Editar</RouterLink>
                  <button class="btn btn-danger btn-sm" @click="confirmDelete(a)">Excluir</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modal de exclusão -->
    <div v-if="deleteTarget" class="modal-overlay" @click.self="deleteTarget = null">
      <div class="modal">
        <h3>Excluir análise?</h3>
        <p>Excluir a análise <strong>{{ deleteTarget.id_amostra }}</strong> também removerá as recomendações associadas.</p>
        <div class="modal-actions">
          <button class="btn btn-secondary" @click="deleteTarget = null">Cancelar</button>
          <button class="btn btn-danger" @click="handleDelete" :disabled="deleting">
            {{ deleting ? 'Excluindo...' : 'Excluir' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Modal de comparação -->
    <div v-if="showComparison && comparisonPair" class="modal-overlay" @click.self="showComparison = false">
      <div class="modal modal-wide">
        <div class="modal-header">
          <h3>Comparação de Análises</h3>
          <button class="btn btn-ghost btn-sm" @click="showComparison = false">Fechar ✕</button>
        </div>
        <div class="comparison-grid">
          <div class="comp-param">Parâmetro</div>
          <div class="comp-header">
            {{ comparisonPair[0].id_amostra }}<br>
            <small>{{ formatDate(comparisonPair[0].data_analise) }}</small>
          </div>
          <div class="comp-header">
            {{ comparisonPair[1].id_amostra }}<br>
            <small>{{ formatDate(comparisonPair[1].data_analise) }}</small>
          </div>
          <div class="comp-header">Variação</div>

          <template v-for="row in compRows" :key="row.key">
            <div class="comp-label">{{ row.label }}</div>
            <div class="comp-val">{{ row.v1 ?? '—' }}</div>
            <div class="comp-val">{{ row.v2 ?? '—' }}</div>
            <div class="comp-delta" :class="deltaClass(row.v1, row.v2, row.higherBetter)">
              {{ deltaArrow(row.v1, row.v2, row.higherBetter) }}
              {{ row.v1 !== null && row.v2 !== null ? Math.abs(Number((row.v2 - row.v1).toFixed(3))) : '—' }}
            </div>
          </template>

          <div class="comp-label comp-score-label">Score de Saúde</div>
          <div class="comp-val comp-score" :style="{ color: scoreColor(calcularScore(comparisonPair[0])) }">
            {{ calcularScore(comparisonPair[0]) }}
          </div>
          <div class="comp-val comp-score" :style="{ color: scoreColor(calcularScore(comparisonPair[1])) }">
            {{ calcularScore(comparisonPair[1]) }}
          </div>
          <div class="comp-delta" :class="deltaClass(calcularScore(comparisonPair[0]), calcularScore(comparisonPair[1]), true)">
            {{ deltaArrow(calcularScore(comparisonPair[0]), calcularScore(comparisonPair[1]), true) }}
            {{ Math.abs(calcularScore(comparisonPair[1]) - calcularScore(comparisonPair[0])) }}
          </div>
        </div>
        <p class="comp-hint">▲ Verde = melhora &nbsp;|&nbsp; ▼ Vermelho = piora em relação à primeira amostra</p>
      </div>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import api from '@/services/api'
import type { SoilAnalysis, Property, Recommendation } from '@/types'
import { calcularScore, scoreColor, scoreLabel } from '@/composables/soilMetrics'

const route = useRoute()
const analyses = ref<SoilAnalysis[]>([])
const properties = ref<Property[]>([])
const loading = ref(true)
const error = ref('')
const filterPropId = ref<number | ''>(route.query.propriedade_id ? Number(route.query.propriedade_id) : '')
const deleteTarget = ref<SoilAnalysis | null>(null)
const deleting = ref(false)
const exporting = ref(false)
const selectedForComparison = ref<number[]>([])
const showComparison = ref(false)

const filtered = computed(() =>
  filterPropId.value ? analyses.value.filter(a => a.propriedade_id === filterPropId.value) : analyses.value
)

const comparisonPair = computed(() => {
  if (selectedForComparison.value.length !== 2) return null
  const [id1, id2] = selectedForComparison.value
  const a = analyses.value.find(x => x.id === id1)
  const b = analyses.value.find(x => x.id === id2)
  return a && b ? [a, b] as const : null
})

const compRows = computed(() => {
  if (!comparisonPair.value) return []
  const [a, b] = comparisonPair.value
  return [
    { key: 'ph', label: 'pH', v1: a.ph, v2: b.ph, higherBetter: true },
    { key: 'mo', label: 'M.O. (%)', v1: a.materia_organica, v2: b.materia_organica, higherBetter: true },
    { key: 'p', label: 'P (mg/dm³)', v1: a.fosforo, v2: b.fosforo, higherBetter: true },
    { key: 'k', label: 'K (cmolc)', v1: a.potassio, v2: b.potassio, higherBetter: true },
    { key: 'ca', label: 'Ca (cmolc)', v1: a.calcio, v2: b.calcio, higherBetter: true },
    { key: 'mg', label: 'Mg (cmolc)', v1: a.magnesio, v2: b.magnesio, higherBetter: true },
  ]
})

function toggleComparison(id: number) {
  const idx = selectedForComparison.value.indexOf(id)
  if (idx >= 0) {
    selectedForComparison.value.splice(idx, 1)
  } else if (selectedForComparison.value.length < 2) {
    selectedForComparison.value.push(id)
  }
}

function deltaArrow(v1: number | null, v2: number | null, higherBetter: boolean): string {
  if (v1 === null || v2 === null) return ''
  if (v2 > v1) return higherBetter ? '▲' : '▼'
  if (v2 < v1) return higherBetter ? '▼' : '▲'
  return '='
}

function deltaClass(v1: number | null, v2: number | null, higherBetter: boolean): string {
  if (v1 === null || v2 === null) return ''
  const improved = higherBetter ? v2 > v1 : v2 < v1
  const worsened = higherBetter ? v2 < v1 : v2 > v1
  if (improved) return 'delta-up'
  if (worsened) return 'delta-down'
  return ''
}

function propName(id: number) {
  return properties.value.find(p => p.id === id)?.nome ?? `#${id}`
}
function formatDate(d: string) {
  return new Date(d).toLocaleDateString('pt-BR')
}
function phClass(ph: number | null) {
  if (ph === null) return ''
  if (ph < 5.5) return 'ph-low'
  if (ph > 7.5) return 'ph-high'
  return 'ph-ok'
}
function recBadgeClass(recs: Recommendation[]) {
  if (recs.some(r => r.prioridade === 'alta')) return 'badge-alta'
  if (recs.some(r => r.prioridade === 'media')) return 'badge-media'
  return 'badge-baixa'
}
function confirmDelete(a: SoilAnalysis) { deleteTarget.value = a }

async function handleDelete() {
  if (!deleteTarget.value) return
  deleting.value = true
  try {
    await api.delete(`/api/analyses/${deleteTarget.value.id}`)
    analyses.value = analyses.value.filter(a => a.id !== deleteTarget.value!.id)
    selectedForComparison.value = selectedForComparison.value.filter(id => id !== deleteTarget.value!.id)
    deleteTarget.value = null
  } catch {
    error.value = 'Erro ao excluir análise'
  } finally {
    deleting.value = false
  }
}

async function exportCSV() {
  exporting.value = true
  try {
    const params: Record<string, unknown> = {}
    if (filterPropId.value) params.propriedade_id = filterPropId.value
    const response = await api.get('/api/analyses/export', { params, responseType: 'blob' })
    const url = URL.createObjectURL(response.data)
    const a = document.createElement('a')
    a.href = url
    a.download = `analises-solo-${new Date().toISOString().slice(0, 10)}.csv`
    a.click()
    URL.revokeObjectURL(url)
  } catch {
    error.value = 'Erro ao exportar CSV'
  } finally {
    exporting.value = false
  }
}

onMounted(async () => {
  try {
    const [aRes, pRes] = await Promise.all([api.get('/api/analyses/'), api.get('/api/properties/')])
    analyses.value = aRes.data
    properties.value = pRes.data
  } catch {
    error.value = 'Erro ao carregar dados'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.empty-state-icon svg { width: 40px; height: 40px; }
.filters-row { display: flex; gap: 12px; align-items: flex-start; flex-wrap: wrap; }
.row-actions { display: flex; gap: 6px; }
.ph-low { color: var(--color-danger); font-weight: 600; }
.ph-high { color: var(--color-warning); font-weight: 600; }
.ph-ok { color: var(--color-success); font-weight: 600; }

.row-selected { background: rgba(74, 222, 128, 0.06) !important; }

.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; z-index: 100; }
.modal { background: var(--color-surface); border-radius: 10px; padding: 28px; max-width: 420px; width: 90%; }
.modal-wide { max-width: 640px !important; }
.modal h3 { font-size: 17px; font-weight: 700; margin-bottom: 10px; }
.modal p { font-size: 14px; color: var(--color-text-muted); margin-bottom: 20px; line-height: 1.6; }
.modal-actions { display: flex; gap: 10px; justify-content: flex-end; }
.modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.modal-header h3 { margin-bottom: 0; }

.comparison-grid {
  display: grid;
  grid-template-columns: 130px 1fr 1fr 80px;
  gap: 0;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  overflow: hidden;
  font-size: 13px;
}
.comp-param, .comp-header {
  padding: 8px 12px;
  background: var(--color-surface-2);
  font-weight: 600;
  font-size: 12px;
  line-height: 1.4;
}
.comp-label, .comp-val, .comp-delta {
  padding: 9px 12px;
  border-top: 1px solid var(--color-border);
}
.comp-label { color: var(--color-text-muted); }
.comp-val { font-weight: 500; }
.comp-score { font-weight: 700; font-size: 16px; }
.comp-score-label { font-weight: 600; color: var(--color-text); }
.comp-delta { font-weight: 700; }
.delta-up { color: #16a34a; }
.delta-down { color: #ef4444; }
.comp-hint { font-size: 11px; color: var(--color-text-muted); margin-top: 12px; margin-bottom: 0; }

.score-cell { display: flex; align-items: center; gap: 6px; }
.score-chip {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 99px;
  font-size: 12px;
  font-weight: 700;
}
.score-word { font-size: 11px; font-weight: 500; }
</style>
