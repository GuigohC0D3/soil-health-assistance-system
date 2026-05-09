import type { SoilAnalysis } from '@/types'

const PH_MIN = 5.5, PH_MAX = 6.5, PH_OTM = 6.0
const MO_MIN = 2.5, MO_OTM = 3.5
const P_MIN = 10.0, P_OTM = 15.0
const K_MIN = 0.15, K_OTM = 0.20
const CA_MIN = 2.0, CA_OTM = 4.0
const MG_MIN = 0.5, MG_OTM = 1.0

export function desvioNorm(
  atual: number,
  minimo: number,
  otimo: number,
  maximo: number | null = null
): number {
  if (maximo !== null && atual > maximo) return -(atual - otimo) / otimo
  if (atual < minimo) return (otimo - atual) / otimo
  return 0
}

export function adqPct(desvio: number): number {
  return Math.max(0, Math.min(100, Math.round((1 - Math.abs(desvio)) * 100)))
}

export function calcularScore(a: SoilAnalysis): number {
  const devs: number[] = []
  if (a.ph != null) devs.push(Math.abs(desvioNorm(a.ph, PH_MIN, PH_OTM, PH_MAX)))
  if (a.materia_organica != null) devs.push(Math.abs(desvioNorm(a.materia_organica, MO_MIN, MO_OTM)))
  if (a.fosforo != null) devs.push(Math.abs(desvioNorm(a.fosforo, P_MIN, P_OTM)))
  if (a.potassio != null) devs.push(Math.abs(desvioNorm(a.potassio, K_MIN, K_OTM)))
  if (a.calcio != null) devs.push(Math.abs(desvioNorm(a.calcio, CA_MIN, CA_OTM)))
  if (a.magnesio != null) devs.push(Math.abs(desvioNorm(a.magnesio, MG_MIN, MG_OTM)))
  if (devs.length === 0) return 0
  const med = devs.reduce((s, d) => s + d, 0) / devs.length
  return Math.max(0, Math.round(100 - med * 100))
}

export function scoreColor(score: number): string {
  if (score >= 75) return '#2d6a4f'
  if (score >= 50) return '#f4a261'
  return '#e63946'
}

export function scoreLabel(score: number): string {
  if (score >= 75) return 'Bom'
  if (score >= 50) return 'Regular'
  return 'Crítico'
}

export function radarAdequacy(a: SoilAnalysis): number[] {
  return [
    a.ph != null ? adqPct(desvioNorm(a.ph, PH_MIN, PH_OTM, PH_MAX)) : 0,
    a.materia_organica != null ? adqPct(desvioNorm(a.materia_organica, MO_MIN, MO_OTM)) : 0,
    a.fosforo != null ? adqPct(desvioNorm(a.fosforo, P_MIN, P_OTM)) : 0,
    a.potassio != null ? adqPct(desvioNorm(a.potassio, K_MIN, K_OTM)) : 0,
    a.calcio != null ? adqPct(desvioNorm(a.calcio, CA_MIN, CA_OTM)) : 0,
    a.magnesio != null ? adqPct(desvioNorm(a.magnesio, MG_MIN, MG_OTM)) : 0,
  ]
}
