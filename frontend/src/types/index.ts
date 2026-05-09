export type UserRole = 'produtor' | 'tecnico' | 'admin'
export type PriorityLevel = 'alta' | 'media' | 'baixa'

export interface User {
  id: number
  nome: string
  email: string
  papel: UserRole
  ativo: boolean
  criado_em: string
}

export interface Property {
  id: number
  nome: string
  area_hectares: number | null
  localizacao: string | null
  cidade: string | null
  estado: string | null
  proprietario_id: number
  criado_em: string
}

export interface Recommendation {
  id: number
  tipo: string
  descricao: string
  prioridade: PriorityLevel
  analise_id: number
  criado_em: string
}

export interface SoilAnalysis {
  id: number
  id_amostra: string
  data_analise: string
  ph: number | null
  materia_organica: number | null
  fosforo: number | null
  potassio: number | null
  calcio: number | null
  magnesio: number | null
  teor_argila: number | null
  cor_munsell: string | null
  observacoes: string | null
  propriedade_id: number
  criado_em: string
  recomendacoes: Recommendation[]
}

export interface LoginRequest {
  email: string
  senha: string
}

export interface RegisterRequest {
  nome: string
  email: string
  senha: string
  papel: UserRole
}

export interface TokenResponse {
  access_token: string
  token_type: string
  user: User
}

export interface PropertyCreate {
  nome: string
  area_hectares?: number | null
  localizacao?: string | null
  cidade?: string | null
  estado?: string | null
}

export interface SoilAnalysisCreate {
  id_amostra: string
  data_analise: string
  ph?: number | null
  materia_organica?: number | null
  fosforo?: number | null
  potassio?: number | null
  calcio?: number | null
  magnesio?: number | null
  teor_argila?: number | null
  cor_munsell?: string | null
  observacoes?: string | null
  propriedade_id: number
}

export interface AlertItem {
  tipo: string
  mensagem: string
  prioridade: 'alta' | 'media'
  propriedade_id: number
  propriedade_nome: string
  analise_id: number | null
}

export interface LimingSimulation {
  antes: {
    v_pct: number
    ph_estimado: number
    necessidade_calagem: number | null
    score_saude: number
  }
  depois: {
    v_pct_simulado: number
    ph_simulado: number
  }
  narrativa: string
}

export interface FertilizerPlan {
  analysis_id: number
  propriedade_nome: string
  area_hectares: number
  calagem: {
    v1_pct: number
    nc_t_ha: number
    nc_total_t: number
  }
  fosfato: {
    p2o5_kg_ha: number
    superfosfato_simples_kg_ha: number
    superfosfato_simples_total_kg: number
    superfosfato_triplo_kg_ha: number
    superfosfato_triplo_total_kg: number
    categoria: string
  }
  potassio: {
    k2o_kg_ha: number
    kcl_kg_ha: number
    kcl_total_kg: number
    categoria: string
  }
  nitrogenio: {
    dose_recomendada: string
  }
}
