<template>
  <AppLayout>
    <div class="page-header">
      <div>
        <h2 class="page-title">Relatórios</h2>
        <p class="page-subtitle">Visão consolidada por propriedade</p>
      </div>
      <button class="btn btn-primary" @click="print">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="15" height="15">
          <polyline points="6 9 6 2 18 2 18 9"/>
          <path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/>
          <rect x="6" y="14" width="12" height="8"/>
        </svg>
        Imprimir
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
            <div class="stat-label">Alertas Críticos</div>
            <div class="stat-value" :style="{ color: criticalRecs > 0 ? 'var(--color-danger)' : 'var(--color-primary)' }">
              {{ criticalRecs }}
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
                  <th>P (mg/dm³)</th><th>K (cmolc)</th><th>Ca (cmolc)</th><th>Mg (cmolc)</th>
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
import api from '@/services/api'
import type { Property, SoilAnalysis, Recommendation } from '@/types'

const properties = ref<Property[]>([])
const selectedPropId = ref<number | ''>('')
const propAnalyses = ref<SoilAnalysis[]>([])
const propRecs = ref<Recommendation[]>([])

const selectedProp = computed(() => properties.value.find(p => p.id === selectedPropId.value))
const today = new Date().toLocaleDateString('pt-BR')
const lastAnalysisDate = computed(() => propAnalyses.value.length ? formatDate(propAnalyses.value[0].data_analise) : '—')
const totalRecs = computed(() => propRecs.value.length)
const criticalRecs = computed(() => propRecs.value.filter(r => r.prioridade === 'alta').length)

function formatDate(d: string) { return new Date(d).toLocaleDateString('pt-BR') }
function priorityLabel(p: string) { return { alta: 'Alta', media: 'Média', baixa: 'Baixa' }[p] ?? p }
function phClass(v: number | null) { if (v === null || v === undefined) return ''; return v < 5.5 ? 'val-low' : v > 7.5 ? 'val-warn' : 'val-ok' }
function moClass(v: number | null) { if (v === null || v === undefined) return ''; return v < 2.5 ? 'val-low' : 'val-ok' }
function pClass(v: number | null) { if (v === null || v === undefined) return ''; return v < 10 ? 'val-low' : 'val-ok' }
function kClass(v: number | null) { if (v === null || v === undefined) return ''; return v < 0.15 ? 'val-low' : 'val-ok' }
function print() { window.print() }

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

</style>
