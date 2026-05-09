<template>
  <div v-if="sorted.length >= 2">
    <Line :data="chartData" :options="chartOptions" />
  </div>
  <p v-else class="hint">Registre pelo menos 2 análises para ver a evolução temporal.</p>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js'
import type { SoilAnalysis } from '@/types'
import { calcularScore, scoreColor } from '@/composables/soilMetrics'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler)

const props = defineProps<{ analyses: SoilAnalysis[] }>()

const sorted = computed(() =>
  [...props.analyses].sort(
    (a, b) => new Date(a.data_analise).getTime() - new Date(b.data_analise).getTime()
  )
)

const chartData = computed(() => ({
  labels: sorted.value.map(a => new Date(a.data_analise).toLocaleDateString('pt-BR')),
  datasets: [
    {
      label: 'Score de Saúde do Solo',
      data: sorted.value.map(a => calcularScore(a)),
      fill: true,
      backgroundColor: 'rgba(45, 106, 79, 0.10)',
      borderColor: '#2d6a4f',
      pointBackgroundColor: sorted.value.map(a => scoreColor(calcularScore(a))),
      pointBorderColor: '#ffffff',
      pointBorderWidth: 2,
      pointRadius: 6,
      pointHoverRadius: 8,
      tension: 0.3,
    },
  ],
}))

const chartOptions = {
  responsive: true,
  plugins: {
    legend: { display: false },
    tooltip: {
      callbacks: {
        label: (ctx: { raw: unknown }) => `Score: ${Number(ctx.raw)}/100`,
      },
    },
  },
  scales: {
    y: {
      min: 0,
      max: 100,
      ticks: { color: '#5a7a5a' },
      grid: { color: '#e8f0e8' },
      title: {
        display: true,
        text: 'Score de Saúde (0–100)',
        color: '#5a7a5a',
        font: { size: 12 },
      },
    },
    x: {
      ticks: { color: '#5a7a5a' },
      grid: { color: '#f0f4f0' },
    },
  },
}
</script>

<style scoped>
.hint {
  color: var(--color-text-muted);
  font-size: 13px;
  text-align: center;
  padding: 24px 0;
}
</style>
