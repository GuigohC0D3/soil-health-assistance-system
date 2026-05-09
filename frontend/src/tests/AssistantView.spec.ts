import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import api from '@/services/api'
import AssistantView from '@/views/AssistantView.vue'

const AppLayoutStub = { template: '<div><slot /></div>' }

describe('AssistantView', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    ;(api.get as any).mockResolvedValue({ data: [] })
  })

  it('renders suggested question chips', async () => {
    const wrapper = mount(AssistantView, {
      global: { stubs: { AppLayout: AppLayoutStub } },
    })
    await flushPromises()
    expect(wrapper.findAll('.chip').length).toBe(3)
  })

  it('clicking chip fills input', async () => {
    const wrapper = mount(AssistantView, {
      global: { stubs: { AppLayout: AppLayoutStub } },
    })
    await flushPromises()
    await wrapper.findAll('.chip')[0].trigger('click')
    const textarea = wrapper.find('textarea')
    expect((textarea.element as HTMLTextAreaElement).value).toBe(
      'Qual propriedade tem pior tendência de fósforo?'
    )
  })

  it('sending message calls api.post and shows reply', async () => {
    ;(api.post as any).mockResolvedValueOnce({
      data: { reply: 'Soja tem V% baixo.' },
    })
    const wrapper = mount(AssistantView, {
      global: { stubs: { AppLayout: AppLayoutStub } },
    })
    await flushPromises()

    const textarea = wrapper.find('textarea')
    await textarea.setValue('Qual o score?')

    await wrapper.find('.send-btn').trigger('click')
    await flushPromises()

    expect(api.post).toHaveBeenCalledWith('/api/assistant/chat', {
      message: 'Qual o score?',
      property_id: null,
    })
    expect(wrapper.text()).toContain('Soja tem V% baixo.')
  })

  it('api error shows error message bubble', async () => {
    ;(api.post as any).mockRejectedValueOnce(new Error('fail'))
    const wrapper = mount(AssistantView, {
      global: { stubs: { AppLayout: AppLayoutStub } },
    })
    await flushPromises()

    const textarea = wrapper.find('textarea')
    await textarea.setValue('Qual o score?')
    await wrapper.find('.send-btn').trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('erro')
  })
})
