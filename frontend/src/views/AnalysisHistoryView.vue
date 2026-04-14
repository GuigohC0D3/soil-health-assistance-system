<template>
  <AppLayout>
    <div class="page-header">
      <div>
        <h2 class="page-title">Histórico de Análises</h2>
        <p class="page-subtitle">Todas as análises de solo registradas</p>
      </div>
      <RouterLink to="/analyses/new" class="btn btn-primary">+ Nova Análise</RouterLink>
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
          <button class="btn btn-secondary" style="align-self: flex-end;" @click="filterPropId = ''">Limpar</button>
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
              <th>Amostra</th>
              <th>Propriedade</th>
              <th>Data</th>
              <th>pH</th>
              <th>M.O. (%)</th>
              <th>P (mg/dm³)</th>
              <th>K (cmolc)</th>
              <th>Recs.</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="a in filtered" :key="a.id">
              <td><strong>{{ a.id_amostra }}</strong></td>
              <td>{{ propName(a.propriedade_id) }}</td>
              <td>{{ formatDate(a.data_analise) }}</td>
              <td><span :class="phClass(a.ph)">{{ a.ph ?? '—' }}</span></td>
              <td>{{ a.materia_organica ?? '—' }}</td>
              <td>{{ a.fosforo ?? '—' }}</td>
              <td>{{ a.potassio ?? '—' }}</td>
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
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import api from '@/services/api'
import type { SoilAnalysis, Property, Recommendation } from '@/types'

const route = useRoute()
const analyses = ref<SoilAnalysis[]>([])
const properties = ref<Property[]>([])
const loading = ref(true)
const error = ref('')
const filterPropId = ref<number | ''>(route.query.propriedade_id ? Number(route.query.propriedade_id) : '')
const deleteTarget = ref<SoilAnalysis | null>(null)
const deleting = ref(false)

const filtered = computed(() =>
  filterPropId.value ? analyses.value.filter(a => a.propriedade_id === filterPropId.value) : analyses.value
)

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
    deleteTarget.value = null
  } catch {
    error.value = 'Erro ao excluir análise'
  } finally {
    deleting.value = false
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
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; z-index: 100; }
.modal { background: var(--color-surface); border-radius: 10px; padding: 28px; max-width: 420px; width: 90%; }
.modal h3 { font-size: 17px; font-weight: 700; margin-bottom: 10px; }
.modal p { font-size: 14px; color: var(--color-text-muted); margin-bottom: 20px; line-height: 1.6; }
.modal-actions { display: flex; gap: 10px; justify-content: flex-end; }
</style>
