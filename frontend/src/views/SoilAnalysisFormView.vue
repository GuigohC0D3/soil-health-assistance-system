<template>
  <AppLayout>
    <div class="page-header">
      <div>
        <h2 class="page-title">{{ isEdit ? 'Editar Análise' : 'Nova Análise de Solo' }}</h2>
        <p class="page-subtitle">Preencha os resultados da análise laboratorial</p>
      </div>
      <RouterLink to="/analyses" class="btn btn-ghost">← Voltar</RouterLink>
    </div>

    <div class="card" style="max-width: 700px;">
      <div class="card-body">
        <div v-if="error" class="alert alert-error">{{ error }}</div>

        <form @submit.prevent="handleSubmit">
          <h3 class="section-title">Identificação</h3>

          <div class="grid-2">
            <div class="form-group">
              <label class="form-label">Propriedade *</label>
              <select v-model.number="form.propriedade_id" class="form-control" required>
                <option value="" disabled>Selecione a propriedade</option>
                <option v-for="p in properties" :key="p.id" :value="p.id">{{ p.nome }}</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">ID da Amostra *</label>
              <input v-model="form.id_amostra" type="text" class="form-control" placeholder="Ex: AM-2024-001" required />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Data da Análise *</label>
            <input v-model="form.data_analise" type="date" class="form-control" required />
          </div>

          <h3 class="section-title" style="margin-top: 20px;">Resultados da Análise</h3>
          <p class="section-hint">Deixe em branco os campos não analisados</p>

          <div class="grid-3">
            <div class="form-group">
              <label class="form-label">pH</label>
              <input v-model.number="form.ph" type="number" step="0.1" min="0" max="14" class="form-control" placeholder="Ex: 6.2" />
              <small class="field-hint">Faixa ideal: 5.5 – 6.5</small>
            </div>
            <div class="form-group">
              <label class="form-label">Matéria Orgânica (%)</label>
              <input v-model.number="form.materia_organica" type="number" step="0.01" min="0" class="form-control" placeholder="Ex: 3.5" />
              <small class="field-hint">Ideal: &gt; 2.5%</small>
            </div>
            <div class="form-group">
              <label class="form-label">Fósforo (mg/dm³)</label>
              <input v-model.number="form.fosforo" type="number" step="0.1" min="0" class="form-control" placeholder="Ex: 18.5" />
              <small class="field-hint">Ideal: &gt; 10 mg/dm³</small>
            </div>
            <div class="form-group">
              <label class="form-label">Potássio (cmolc/dm³)</label>
              <input v-model.number="form.potassio" type="number" step="0.01" min="0" class="form-control" placeholder="Ex: 0.28" />
              <small class="field-hint">Ideal: &gt; 0.15</small>
            </div>
            <div class="form-group">
              <label class="form-label">Cálcio (cmolc/dm³)</label>
              <input v-model.number="form.calcio" type="number" step="0.1" min="0" class="form-control" placeholder="Ex: 4.1" />
              <small class="field-hint">Ideal: &gt; 2.0</small>
            </div>
            <div class="form-group">
              <label class="form-label">Magnésio (cmolc/dm³)</label>
              <input v-model.number="form.magnesio" type="number" step="0.01" min="0" class="form-control" placeholder="Ex: 1.2" />
              <small class="field-hint">Ideal: &gt; 0.5</small>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Observações</label>
            <textarea v-model="form.observacoes" class="form-control" placeholder="Observações adicionais sobre a amostra ou condição do solo..." rows="3"></textarea>
          </div>

          <div class="rec-notice" v-if="!isEdit">
            As recomendações de manejo serão geradas automaticamente após o registro.
          </div>

          <div class="form-actions">
            <RouterLink to="/analyses" class="btn btn-secondary">Cancelar</RouterLink>
            <button type="submit" class="btn btn-primary" :disabled="saving">
              {{ saving ? 'Salvando...' : (isEdit ? 'Salvar Alterações' : 'Registrar Análise') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import api from '@/services/api'
import type { Property } from '@/types'

const route = useRoute()
const router = useRouter()

const isEdit = computed(() => !!route.params.id)
const saving = ref(false)
const error = ref('')
const properties = ref<Property[]>([])

const form = ref({
  propriedade_id: '' as number | '',
  id_amostra: '',
  data_analise: new Date().toISOString().split('T')[0],
  ph: null as number | null,
  materia_organica: null as number | null,
  fosforo: null as number | null,
  potassio: null as number | null,
  calcio: null as number | null,
  magnesio: null as number | null,
  observacoes: '',
})

onMounted(async () => {
  const { data } = await api.get('/api/properties/')
  properties.value = data

  const qPropId = route.query.propriedade_id
  if (qPropId) form.value.propriedade_id = Number(qPropId)

  if (isEdit.value) {
    try {
      const { data: analysis } = await api.get(`/api/analyses/${route.params.id}`)
      form.value = {
        propriedade_id: analysis.propriedade_id,
        id_amostra: analysis.id_amostra,
        data_analise: analysis.data_analise,
        ph: analysis.ph,
        materia_organica: analysis.materia_organica,
        fosforo: analysis.fosforo,
        potassio: analysis.potassio,
        calcio: analysis.calcio,
        magnesio: analysis.magnesio,
        observacoes: analysis.observacoes ?? '',
      }
    } catch {
      error.value = 'Erro ao carregar análise'
    }
  }
})

async function handleSubmit() {
  saving.value = true
  error.value = ''
  const payload = {
    ...form.value,
    observacoes: form.value.observacoes || null,
    propriedade_id: Number(form.value.propriedade_id),
  }
  try {
    if (isEdit.value) {
      await api.put(`/api/analyses/${route.params.id}`, payload)
    } else {
      await api.post('/api/analyses/', payload)
    }
    router.push('/analyses')
  } catch (e: any) {
    error.value = e.response?.data?.detail ?? 'Erro ao salvar análise'
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.section-title { font-size: 13px; font-weight: 700; color: var(--color-primary); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 14px; border-bottom: 1px solid var(--color-border); padding-bottom: 8px; }
.section-hint { font-size: 12px; color: var(--color-text-muted); margin-top: -10px; margin-bottom: 14px; }
.field-hint { font-size: 11px; color: var(--color-text-muted); margin-top: 3px; display: block; }
.rec-notice { background: #f0f7f0; border: 1px solid var(--color-border); border-radius: 6px; padding: 10px 14px; font-size: 13px; color: var(--color-text-muted); margin-bottom: 16px; }
.form-actions { display: flex; gap: 10px; justify-content: flex-end; margin-top: 8px; }
</style>
