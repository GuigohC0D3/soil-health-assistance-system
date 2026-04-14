<template>
  <AppLayout>
    <div class="page-header">
      <div>
        <h2 class="page-title">{{ isEdit ? 'Editar Propriedade' : 'Nova Propriedade' }}</h2>
        <p class="page-subtitle">{{ isEdit ? 'Atualize os dados da propriedade' : 'Preencha os dados da propriedade agrícola' }}</p>
      </div>
      <RouterLink to="/properties" class="btn btn-ghost">← Voltar</RouterLink>
    </div>

    <div class="card" style="max-width: 600px;">
      <div class="card-body">
        <div v-if="error" class="alert alert-error">{{ error }}</div>

        <form @submit.prevent="handleSubmit">
          <div class="form-group">
            <label class="form-label">Nome da Propriedade *</label>
            <input v-model="form.nome" type="text" class="form-control" placeholder="Ex: Fazenda Boa Vista" required />
          </div>

          <div class="form-group">
            <label class="form-label">Área (hectares)</label>
            <input v-model.number="form.area_hectares" type="number" step="0.01" min="0" class="form-control" placeholder="Ex: 120.5" />
          </div>

          <div class="grid-2">
            <div class="form-group">
              <label class="form-label">Cidade</label>
              <input v-model="form.cidade" type="text" class="form-control" placeholder="Ex: Rondonópolis" />
            </div>
            <div class="form-group">
              <label class="form-label">Estado (UF)</label>
              <input v-model="form.estado" type="text" class="form-control" placeholder="MT" maxlength="2" style="text-transform: uppercase;" />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Localização / Endereço</label>
            <input v-model="form.localizacao" type="text" class="form-control" placeholder="Ex: Rodovia BR-364, km 45" />
          </div>

          <div class="form-actions">
            <RouterLink to="/properties" class="btn btn-secondary">Cancelar</RouterLink>
            <button type="submit" class="btn btn-primary" :disabled="saving">
              {{ saving ? 'Salvando...' : (isEdit ? 'Salvar Alterações' : 'Cadastrar Propriedade') }}
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

const route = useRoute()
const router = useRouter()

const isEdit = computed(() => !!route.params.id)
const saving = ref(false)
const error = ref('')

const form = ref({
  nome: '',
  area_hectares: null as number | null,
  localizacao: '',
  cidade: '',
  estado: '',
})

onMounted(async () => {
  if (isEdit.value) {
    try {
      const { data } = await api.get(`/api/properties/${route.params.id}`)
      form.value = {
        nome: data.nome,
        area_hectares: data.area_hectares,
        localizacao: data.localizacao ?? '',
        cidade: data.cidade ?? '',
        estado: data.estado ?? '',
      }
    } catch {
      error.value = 'Erro ao carregar propriedade'
    }
  }
})

async function handleSubmit() {
  saving.value = true
  error.value = ''
  const payload = {
    nome: form.value.nome,
    area_hectares: form.value.area_hectares || null,
    localizacao: form.value.localizacao || null,
    cidade: form.value.cidade || null,
    estado: form.value.estado?.toUpperCase() || null,
  }
  try {
    if (isEdit.value) {
      await api.put(`/api/properties/${route.params.id}`, payload)
    } else {
      await api.post('/api/properties/', payload)
    }
    router.push('/properties')
  } catch (e: any) {
    error.value = e.response?.data?.detail ?? 'Erro ao salvar propriedade'
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.form-actions { display: flex; gap: 10px; justify-content: flex-end; margin-top: 8px; }
</style>
