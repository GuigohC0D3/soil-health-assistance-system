<template>
  <AppLayout>
    <div class="page-header">
      <div>
        <h2 class="page-title">Assistente</h2>
        <p class="page-subtitle">Tire dúvidas sobre suas análises de solo</p>
      </div>
    </div>

    <div class="card filters-card">
      <div class="card-body" style="padding: 14px 20px;">
        <div class="form-group" style="margin:0; max-width: 280px;">
          <label class="form-label">Filtrar por Propriedade</label>
          <select v-model="propertyId" class="form-control">
            <option :value="null">Todas</option>
            <option v-for="p in properties" :key="p.id" :value="p.id">{{ p.nome }}</option>
          </select>
        </div>
      </div>
    </div>

    <div class="chat-card card">
      <div class="chat-messages" ref="messagesRef">
        <div class="welcome-msg" v-if="messages.length === 0">
          <p>Olá! Pergunte sobre suas análises de solo, tendências de nutrientes, ou recomendações de manejo.</p>
        </div>

        <div
          v-for="(msg, i) in messages"
          :key="i"
          class="chat-bubble"
          :class="msg.role === 'user' ? 'bubble-user' : 'bubble-assistant'"
        >
          <div class="bubble-content">{{ msg.content }}</div>
        </div>

        <div v-if="loading" class="chat-bubble bubble-assistant">
          <div class="bubble-content loading-indicator">
            <span class="dot-pulse"></span>
          </div>
        </div>
      </div>

      <div class="suggested-chips">
        <button
          v-for="(q, i) in suggestedQuestions"
          :key="i"
          class="chip"
          @click="inputMessage = q"
        >
          {{ q }}
        </button>
      </div>

      <div class="chat-input-row">
        <textarea
          v-model="inputMessage"
          class="chat-input"
          placeholder="Digite sua pergunta..."
          rows="2"
          @keydown.enter.exact.prevent="sendMessage"
        ></textarea>
        <button class="btn btn-primary send-btn" :disabled="!inputMessage.trim() || loading" @click="sendMessage">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="18" height="18">
            <line x1="22" y1="2" x2="11" y2="13"/>
            <polygon points="22 2 15 22 11 13 2 9 22 2"/>
          </svg>
        </button>
      </div>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, nextTick, onMounted } from 'vue'
import AppLayout from '@/components/AppLayout.vue'
import api from '@/services/api'
import type { Property } from '@/types'

const properties = ref<Property[]>([])
const propertyId = ref<number | null>(null)
const messages = ref<{ role: 'user' | 'assistant'; content: string }[]>([])
const inputMessage = ref('')
const loading = ref(false)
const messagesRef = ref<HTMLElement | null>(null)

const suggestedQuestions = [
  'Qual propriedade tem pior tendência de fósforo?',
  'Quando precisarei calcionar novamente?',
  'Qual é o score de saúde atual de cada propriedade?',
]

async function sendMessage() {
  const text = inputMessage.value.trim()
  if (!text || loading.value) return

  messages.value.push({ role: 'user', content: text })
  inputMessage.value = ''
  loading.value = true
  await scrollToBottom()

  try {
    const { data } = await api.post('/api/assistant/chat', {
      message: text,
      property_id: propertyId.value,
    })
    messages.value.push({ role: 'assistant', content: data.reply })
  } catch {
    messages.value.push({ role: 'assistant', content: 'Desculpe, ocorreu um erro ao processar sua pergunta. Tente novamente.' })
  } finally {
    loading.value = false
    await scrollToBottom()
  }
}

async function scrollToBottom() {
  await nextTick()
  if (messagesRef.value) {
    messagesRef.value.scrollTop = messagesRef.value.scrollHeight
  }
}

onMounted(async () => {
  try {
    const { data } = await api.get('/api/properties/')
    properties.value = data
  } catch {
    // properties will be empty
  }
})
</script>

<style scoped>
.filters-card { margin-bottom: 20px; }

.chat-card {
  display: flex;
  flex-direction: column;
  max-width: 760px;
  margin: 0 auto;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 320px;
  max-height: 480px;
}

.welcome-msg {
  text-align: center;
  color: var(--color-text-muted);
  font-size: 14px;
  padding: 40px 20px;
}

.chat-bubble {
  display: flex;
}
.bubble-user { justify-content: flex-end; }
.bubble-assistant { justify-content: flex-start; }

.bubble-content {
  max-width: 80%;
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 13.5px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}
.bubble-user .bubble-content {
  background: #2d6a4f;
  color: #fff;
  border-bottom-right-radius: 4px;
}
.bubble-assistant .bubble-content {
  background: var(--color-surface-2);
  color: var(--color-text);
  border-bottom-left-radius: 4px;
}

.loading-indicator {
  display: flex;
  align-items: center;
  padding: 12px 16px;
}

.dot-pulse {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-text-muted);
  animation: pulse 1.2s ease-in-out infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 0.3; transform: scale(0.8); }
  50% { opacity: 1; transform: scale(1); }
}

.suggested-chips {
  display: flex;
  gap: 8px;
  padding: 8px 20px;
  flex-wrap: wrap;
  border-top: 1px solid var(--color-border);
}

.chip {
  background: transparent;
  border: 1px solid var(--color-border);
  border-radius: 99px;
  padding: 5px 12px;
  font-size: 11.5px;
  color: var(--color-text-muted);
  cursor: pointer;
  white-space: nowrap;
  transition: background 0.12s, color 0.12s;
}
.chip:hover {
  background: var(--color-surface-2);
  color: var(--color-text);
}

.chat-input-row {
  display: flex;
  gap: 10px;
  padding: 12px 20px;
  border-top: 1px solid var(--color-border);
  align-items: flex-end;
}

.chat-input {
  flex: 1;
  resize: none;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  padding: 10px 14px;
  font-family: inherit;
  font-size: 13px;
  background: var(--color-surface-2);
  color: var(--color-text);
  outline: none;
  transition: border-color 0.12s;
}
.chat-input:focus {
  border-color: var(--color-primary);
}

.send-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px 14px;
  flex-shrink: 0;
}
</style>
