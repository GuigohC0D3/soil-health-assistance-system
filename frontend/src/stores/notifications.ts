import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'
import type { AlertItem } from '@/types'

export const useNotificationsStore = defineStore('notifications', () => {
  const alerts = ref<AlertItem[]>([])
  const loaded = ref(false)

  const criticalCount = computed(() => alerts.value.filter(a => a.prioridade === 'alta').length)
  const totalCount = computed(() => alerts.value.length)

  async function fetchAlerts() {
    try {
      const { data } = await api.get<AlertItem[]>('/api/notifications/')
      alerts.value = data
      loaded.value = true
    } catch {
      // silently fail — notifications are non-critical UI
    }
  }

  function dismiss(alert: AlertItem) {
    alerts.value = alerts.value.filter(a => a !== alert)
  }

  function clear() {
    alerts.value = []
    loaded.value = false
  }

  return { alerts, loaded, criticalCount, totalCount, fetchAlerts, dismiss, clear }
})
