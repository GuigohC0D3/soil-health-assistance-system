<template>
  <AppLayout>
    <div class="page-header">
      <div>
        <h2 class="page-title">Calculadora de Insumos</h2>
        <p class="page-subtitle">Plano de adubação e calagem baseado na análise de solo</p>
      </div>
      <button v-if="plan" class="btn btn-secondary" @click="printPlan">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15" style="margin-right:4px;">
          <polyline points="6 9 6 2 18 2 18 9"/>
          <path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/>
          <rect x="6" y="14" width="12" height="8"/>
        </svg>
        Imprimir Plano
      </button>
    </div>

    <!-- Seletores -->
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
            <select v-model="selectedAnalysisId" class="form-control">
              <option value="">Selecione a análise...</option>
              <option v-for="a in propAnalyses" :key="a.id" :value="a.id">
                {{ a.id_amostra }} — {{ formatDate(a.data_analise) }}
              </option>
            </select>
          </div>
          <button
            class="btn btn-primary"
            style="align-self:flex-end;"
            :disabled="!selectedAnalysisId || loading"
            @click="calculate"
          >
            {{ loading ? 'Calculando...' : 'Calcular Plano' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="error" class="alert alert-error" style="margin-bottom:16px;">{{ error }}</div>

    <!-- Preços editáveis -->
    <div v-if="plan" class="card" style="margin-bottom:20px;">
      <div class="card-header">Preços dos Insumos (R$) — Ajuste conforme sua região</div>
      <div class="card-body">
        <div class="price-grid">
          <div class="form-group" style="margin:0;">
            <label class="form-label">Calcário (R$/ton)</label>
            <input v-model.number="prices.calcario" type="number" class="form-control" min="0" step="10" />
          </div>
          <div class="form-group" style="margin:0;">
            <label class="form-label">Superfosfato Simples (R$/kg)</label>
            <input v-model.number="prices.ss" type="number" class="form-control" min="0" step="0.10" />
          </div>
          <div class="form-group" style="margin:0;">
            <label class="form-label">Superfosfato Triplo (R$/kg)</label>
            <input v-model.number="prices.st" type="number" class="form-control" min="0" step="0.10" />
          </div>
          <div class="form-group" style="margin:0;">
            <label class="form-label">Cloreto de Potássio (R$/kg)</label>
            <input v-model.number="prices.kcl" type="number" class="form-control" min="0" step="0.10" />
          </div>
        </div>
      </div>
    </div>

    <!-- Plano de Adubação -->
    <div v-if="plan" id="plano-adubacao">
      <div class="card" style="margin-bottom:16px;">
        <div class="card-body" style="padding:16px 20px;">
          <div style="font-size:16px;font-weight:700;">Plano de Adubação — {{ plan.propriedade_nome }}</div>
          <div style="font-size:13px;color:var(--color-text-muted);margin-top:4px;">
            Área: <strong>{{ plan.area_hectares }} ha</strong> &nbsp;|&nbsp; Gerado em: {{ today }}
          </div>
        </div>
      </div>

      <div class="grid-2" style="margin-bottom:16px;">
        <!-- Calagem -->
        <div class="card insumo-card">
          <div class="card-header">
            <span>Calagem (Calcário Calcítico)</span>
            <span class="badge" :class="plan.calagem.nc_t_ha > 0 ? 'badge-alta' : 'badge-baixa'">
              {{ plan.calagem.nc_t_ha > 0 ? 'Necessária' : 'Não necessária' }}
            </span>
          </div>
          <div class="card-body">
            <div class="insumo-row">
              <span class="insumo-label">Saturação de bases atual (V%):</span>
              <span class="insumo-val">{{ plan.calagem.v1_pct }}%</span>
            </div>
            <div class="insumo-row">
              <span class="insumo-label">Necessidade de calagem (NC):</span>
              <span class="insumo-val highlight">{{ plan.calagem.nc_t_ha }} t/ha</span>
            </div>
            <div class="insumo-row">
              <span class="insumo-label">Total para a propriedade:</span>
              <span class="insumo-val">{{ plan.calagem.nc_total_t }} toneladas</span>
            </div>
            <div class="insumo-cost">
              Custo estimado: <strong>{{ formatBRL(plan.calagem.nc_total_t * prices.calcario) }}</strong>
              <span class="insumo-note">PRNT 90%, V2=70%</span>
            </div>
          </div>
        </div>

        <!-- Fosfato -->
        <div class="card insumo-card">
          <div class="card-header">
            <span>Fosfatagem (P₂O₅)</span>
            <span class="badge" :class="badgeForCat(plan.fosfato.categoria)">
              {{ plan.fosfato.categoria }}
            </span>
          </div>
          <div class="card-body">
            <div class="insumo-row">
              <span class="insumo-label">P₂O₅ necessário:</span>
              <span class="insumo-val highlight">{{ plan.fosfato.p2o5_kg_ha }} kg/ha</span>
            </div>
            <div class="insumo-separator">Superfosfato Simples — SS (18% P₂O₅)</div>
            <div class="insumo-row">
              <span class="insumo-label">Dose SS:</span>
              <span class="insumo-val">{{ plan.fosfato.superfosfato_simples_kg_ha }} kg/ha</span>
            </div>
            <div class="insumo-row">
              <span class="insumo-label">Total SS:</span>
              <span class="insumo-val">{{ plan.fosfato.superfosfato_simples_total_kg }} kg</span>
            </div>
            <div class="insumo-cost">
              Custo SS: <strong>{{ formatBRL(plan.fosfato.superfosfato_simples_total_kg * prices.ss) }}</strong>
            </div>
            <div class="insumo-separator">ou Superfosfato Triplo — ST (45% P₂O₅)</div>
            <div class="insumo-row">
              <span class="insumo-label">Total ST:</span>
              <span class="insumo-val">{{ plan.fosfato.superfosfato_triplo_total_kg }} kg</span>
            </div>
            <div class="insumo-cost">
              Custo ST: <strong>{{ formatBRL(plan.fosfato.superfosfato_triplo_total_kg * prices.st) }}</strong>
            </div>
          </div>
        </div>

        <!-- Potássio -->
        <div class="card insumo-card">
          <div class="card-header">
            <span>Potassagem (K₂O)</span>
            <span class="badge" :class="badgeForCat(plan.potassio.categoria)">
              {{ plan.potassio.categoria }}
            </span>
          </div>
          <div class="card-body">
            <div class="insumo-row">
              <span class="insumo-label">K₂O necessário:</span>
              <span class="insumo-val highlight">{{ plan.potassio.k2o_kg_ha }} kg/ha</span>
            </div>
            <div class="insumo-row">
              <span class="insumo-label">Cloreto de Potássio (KCl 60%):</span>
              <span class="insumo-val">{{ plan.potassio.kcl_kg_ha }} kg/ha</span>
            </div>
            <div class="insumo-row">
              <span class="insumo-label">Total KCl:</span>
              <span class="insumo-val">{{ plan.potassio.kcl_total_kg }} kg</span>
            </div>
            <div class="insumo-cost">
              Custo estimado: <strong>{{ formatBRL(plan.potassio.kcl_total_kg * prices.kcl) }}</strong>
            </div>
          </div>
        </div>

        <!-- Nitrogênio -->
        <div class="card insumo-card">
          <div class="card-header">
            <span>Nitrogênio (N)</span>
            <span class="badge" :class="badgeForDose(plan.nitrogenio.dose_recomendada)">
              Dose {{ plan.nitrogenio.dose_recomendada }}
            </span>
          </div>
          <div class="card-body">
            <div v-if="plan.nitrogenio.dose_recomendada === 'alta'" class="n-desc">
              Matéria orgânica muito baixa (&lt;1,5%). Recomendada <strong>dose alta de N</strong>
              (120–160 kg N/ha/ciclo). Priorizar adubação nitrogenada de cobertura.
            </div>
            <div v-else-if="plan.nitrogenio.dose_recomendada === 'media'" class="n-desc">
              Matéria orgânica moderada (1,5–2,5%). Recomendada <strong>dose média de N</strong>
              (80–120 kg N/ha/ciclo). Fracionar em 2–3 aplicações.
            </div>
            <div v-else class="n-desc">
              Matéria orgânica adequada (&gt;2,5%). Recomendada <strong>dose de manutenção de N</strong>
              (40–80 kg N/ha/ciclo). Monitorar continuamente a mineralização.
            </div>
            <div class="n-note">
              * Dose de N deve ser ajustada conforme cultivo, histórico da área e análise foliar.
            </div>
          </div>
        </div>
      </div>

      <!-- Resumo de custos -->
      <div class="card">
        <div class="card-header">Resumo de Custos Estimados</div>
        <div class="card-body">
          <div class="cost-table">
            <div class="cost-row">
              <span>Calcário Calcítico</span>
              <span>{{ formatBRL(plan.calagem.nc_total_t * prices.calcario) }}</span>
            </div>
            <div class="cost-row">
              <span>Superfosfato Simples</span>
              <span>{{ formatBRL(plan.fosfato.superfosfato_simples_total_kg * prices.ss) }}</span>
            </div>
            <div class="cost-row">
              <span>Cloreto de Potássio</span>
              <span>{{ formatBRL(plan.potassio.kcl_total_kg * prices.kcl) }}</span>
            </div>
            <div class="cost-row cost-total">
              <span>Total Estimado (SS + KCl + Cal.)</span>
              <span>{{ formatBRL(totalCost) }}</span>
            </div>
          </div>
          <p class="cost-disclaimer">
            * Valores estimativos. Consulte fornecedores locais para preços atualizados.
            Metodologia baseada em Embrapa/IAC para solos do Cerrado. PRNT 90%, V₂ alvo = 70%.
          </p>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import AppLayout from '@/components/AppLayout.vue'
import api from '@/services/api'
import type { Property, SoilAnalysis, FertilizerPlan } from '@/types'

const properties = ref<Property[]>([])
const propAnalyses = ref<SoilAnalysis[]>([])
const selectedPropId = ref<number | ''>('')
const selectedAnalysisId = ref<number | ''>('')
const plan = ref<FertilizerPlan | null>(null)
const loading = ref(false)
const error = ref('')
const today = new Date().toLocaleDateString('pt-BR')

const prices = ref({
  calcario: 180,
  ss: 2.20,
  st: 3.80,
  kcl: 3.50,
})

const totalCost = computed(() => {
  if (!plan.value) return 0
  return (
    plan.value.calagem.nc_total_t * prices.value.calcario +
    plan.value.fosfato.superfosfato_simples_total_kg * prices.value.ss +
    plan.value.potassio.kcl_total_kg * prices.value.kcl
  )
})

function formatDate(d: string) {
  return new Date(d).toLocaleDateString('pt-BR')
}
function formatBRL(v: number) {
  return v.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}
function printPlan() { window.print() }

function badgeForCat(cat: string) {
  if (cat === 'deficiente') return 'badge-alta'
  if (cat === 'baixo') return 'badge-media'
  return 'badge-baixa'
}
function badgeForDose(dose: string) {
  if (dose === 'alta') return 'badge-alta'
  if (dose === 'media') return 'badge-media'
  return 'badge-baixa'
}

async function onPropChange() {
  propAnalyses.value = []
  plan.value = null
  selectedAnalysisId.value = ''
  if (!selectedPropId.value) return
  const { data } = await api.get('/api/analyses/', { params: { propriedade_id: selectedPropId.value } })
  propAnalyses.value = data
}

async function calculate() {
  if (!selectedAnalysisId.value) return
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get(`/api/analyses/${selectedAnalysisId.value}/fertilizer-plan`)
    plan.value = data
  } catch {
    error.value = 'Erro ao calcular plano de adubação.'
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  const { data } = await api.get('/api/properties/')
  properties.value = data
})
</script>

<style scoped>
.filters-row { display: flex; gap: 12px; align-items: flex-start; flex-wrap: wrap; }

.price-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}
@media (max-width: 768px) { .price-grid { grid-template-columns: repeat(2, 1fr); } }

.insumo-card { }
.insumo-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 7px;
  font-size: 13px;
}
.insumo-label { color: var(--color-text-muted); }
.insumo-val { font-weight: 600; }
.insumo-val.highlight { color: var(--color-primary); font-size: 15px; }

.insumo-separator {
  font-size: 11px;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 10px 0 7px;
  border-top: 1px solid var(--color-border);
  padding-top: 8px;
}

.insumo-cost {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px dashed var(--color-border);
  font-size: 12px;
  color: var(--color-text-muted);
}
.insumo-cost strong { color: var(--color-text); font-size: 14px; }
.insumo-note { display: block; font-size: 10px; margin-top: 2px; }

.n-desc { font-size: 13px; line-height: 1.7; color: var(--color-text); }
.n-note { font-size: 11px; color: var(--color-text-muted); margin-top: 12px; }

.cost-table { display: flex; flex-direction: column; gap: 6px; }
.cost-row {
  display: flex;
  justify-content: space-between;
  font-size: 13.5px;
  padding: 7px 0;
  border-bottom: 1px solid var(--color-border);
}
.cost-total {
  font-weight: 700;
  font-size: 15px;
  color: var(--color-primary);
  border-bottom: none;
  padding-top: 12px;
}
.cost-disclaimer {
  font-size: 11px;
  color: var(--color-text-muted);
  margin-top: 14px;
  line-height: 1.7;
}

@media print {
  .page-header .btn { display: none !important; }
  .card { break-inside: avoid; }
  .price-grid { display: none; }
}
</style>
