<template>
  <div class="soil-core-viz">
    <div class="viz-title">Perfil Visual do Solo</div>
    <div class="profile-columns">
      <div
        v-for="a in analyses"
        :key="a.id"
        class="profile-layer"
        :style="{ backgroundColor: swatchColor(a.cor_munsell) }"
        :title="a.cor_munsell || ''"
      >
        <span class="layer-label">{{ formatDate(a.data_analise) }} | MO: {{ a.materia_organica ?? '—' }}%</span>
      </div>
    </div>
    <div class="viz-legend">Escuro = alta matéria orgânica</div>
  </div>
</template>

<script setup lang="ts">
import type { SoilAnalysis } from '@/types'

let munsellToRgb255: ((code: string) => [number, number, number]) | null = null
try {
  const munsell = await import('munsell')
  munsellToRgb255 = munsell.munsellToRgb255
} catch {
  // munsell package not available, fallback to default colors
}

const props = defineProps<{ analyses: SoilAnalysis[] }>()

function swatchColor(cor: string | null | undefined): string {
  if (!cor) return '#8B7355'
  if (!munsellToRgb255) return '#8B7355'
  try {
    const [r, g, b] = munsellToRgb255(cor)
    return `rgb(${r},${g},${b})`
  } catch {
    return '#8B7355'
  }
}

function formatDate(d: string): string {
  return new Date(d).toLocaleDateString('pt-BR', { month: '2-digit', year: '2-digit' })
}
</script>

<style scoped>
.soil-core-viz {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 80px;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 10px 6px;
  flex-shrink: 0;
}
.viz-title {
  font-size: 10px;
  font-weight: 700;
  color: var(--color-primary);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-bottom: 8px;
  text-align: center;
}
.profile-columns {
  display: flex;
  flex-direction: column;
  gap: 3px;
  width: 100%;
}
.profile-layer {
  height: 48px;
  border-radius: 4px;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  padding-bottom: 4px;
  transition: background-color 0.3s ease;
}
.layer-label {
  font-size: 8px;
  color: #fff;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.6);
  text-align: center;
  line-height: 1.2;
  max-width: 100%;
  overflow: hidden;
}
.viz-legend {
  font-size: 9px;
  color: var(--color-text-muted);
  margin-top: 6px;
  text-align: center;
}
</style>
