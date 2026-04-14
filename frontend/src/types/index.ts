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
  observacoes?: string | null
  propriedade_id: number
}
