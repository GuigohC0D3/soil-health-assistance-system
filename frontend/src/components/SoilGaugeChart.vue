<template>
  <div class="gauge-wrap">
    <svg class="gauge-svg" viewBox="0 0 120 72">
      <!-- Background arc -->
      <path
        d="M 10 65 A 50 50 0 0 1 110 65"
        fill="none"
        stroke="#e2e8f0"
        stroke-width="10"
        stroke-linecap="round"
      />
      <!-- Filled arc — dasharray drives fill level -->
      <path
        d="M 10 65 A 50 50 0 0 1 110 65"
        fill="none"
        :stroke="gaugeColor"
        stroke-width="10"
        stroke-linecap="round"
        :stroke-dasharray="`${filledLength} ${totalLength}`"
        style="transition: stroke-dasharray 0.8s ease;"
      />
      <!-- Score text -->
      <text x="60" y="56" text-anchor="middle" font-size="20" font-weight="700" :fill="gaugeColor">
        {{ score }}
      </text>
      <text x="60" y="68" text-anchor="middle" font-size="7" fill="#64748b">{{ label }}</text>
    </svg>
    <div class="gauge-legend">
      <span>0</span>
      <span>100</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ score: number }>()

const totalLength = 157
const filledLength = computed(() => (props.score / 100) * totalLength)

const gaugeColor = computed(() => {
  if (props.score >= 75) return '#16a34a'
  if (props.score >= 50) return '#f59e0b'
  return '#ef4444'
})

const label = computed(() => {
  if (props.score >= 75) return 'Bom'
  if (props.score >= 50) return 'Regular'
  return 'Crítico'
})
</script>

<style scoped>
.gauge-wrap { display: flex; flex-direction: column; align-items: center; }
.gauge-svg { width: 160px; height: 96px; }
.gauge-legend {
  display: flex;
  justify-content: space-between;
  width: 130px;
  font-size: 10px;
  color: var(--color-text-muted);
  margin-top: -10px;
}
</style>
