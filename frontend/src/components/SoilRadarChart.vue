<template>
  <div class="radar-wrap">
    <Radar :data="chartData" :options="chartOptions" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Radar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
} from 'chart.js'
import type { SoilAnalysis } from '@/types'
import { radarAdequacy } from '@/composables/soilMetrics'

ChartJS.register(RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend)

const props = defineProps<{ analysis: SoilAnalysis }>()

const chartData = computed(() => ({
  labels: ['pH', 'M.O. (%)', 'Fósforo', 'Potássio', 'Cálcio', 'Magnésio'],
  datasets: [
    {
      label: 'Solo Analisado',
      data: radarAdequacy(props.analysis),
      backgroundColor: 'rgba(45, 106, 79, 0.25)',
      borderColor: '#2d6a4f',
      borderWidth: 2,
      pointBackgroundColor: '#2d6a4f',
      pointRadius: 4,
    },
    {
      label: 'Referência Ideal',
      data: [100, 100, 100, 100, 100, 100],
      backgroundColor: 'rgba(116, 198, 157, 0.08)',
      borderColor: '#74c69d',
      borderWidth: 2,
      borderDash: [5, 5],
      pointRadius: 0,
    },
  ],
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: true,
  plugins: {
    legend: { position: 'top' as const },
    tooltip: {
      callbacks: {
        label: (ctx: { dataset: { label?: string }; raw: unknown }) =>
          `${ctx.dataset.label ?? ''}: ${Number(ctx.raw)}%`,
      },
    },
  },
  scales: {
    r: {
      min: 0,
      max: 100,
      ticks: { stepSize: 25, color: '#5a7a5a', font: { size: 10 } },
      pointLabels: { font: { size: 12 }, color: '#1a2e1a' },
      grid: { color: '#d1e8d8' },
      angleLines: { color: '#d1e8d8' },
    },
  },
}
</script>

<style scoped>
.radar-wrap {
  max-width: 380px;
  margin: 0 auto;
}
</style>
