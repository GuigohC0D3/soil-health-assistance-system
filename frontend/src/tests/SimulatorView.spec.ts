import { describe, it, expect, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import api from '@/services/api'
import SimulatorView from '@/views/SimulatorView.vue'

const AppLayoutStub = { template: '<div><slot /></div>' }

describe('SimulatorView', () => {
  it('fetches properties on mount', async () => {
    ;(api.get as any).mockResolvedValue({ data: [{ id: 1, nome: 'Fazenda A' }] })
    const wrapper = mount(SimulatorView, {
      global: { stubs: { AppLayout: AppLayoutStub } },
    })
    await flushPromises()
    expect(api.get).toHaveBeenCalledWith('/api/properties/')
    const selects = wrapper.findAll('select')
    const propSelect = selects[0]
    const options = propSelect.findAll('option')
    expect(options.length).toBeGreaterThanOrEqual(2)
  })

  it('shows result cards after successful simulation', async () => {
    ;(api.get as any)
      .mockResolvedValueOnce({ data: [{ id: 1, nome: 'Fazenda A' }] })
      .mockResolvedValueOnce({
        data: [{ id: 10, id_amostra: 'AM-001', data_analise: '2024-01-15' }],
      })
    ;(api.post as any).mockResolvedValueOnce({
      data: {
        antes: { v_pct: 40, ph_estimado: 5.2, necessidade_calagem: 1.5, score_saude: 55 },
        depois: { v_pct_simulado: 72, ph_simulado: 5.9 },
        narrativa: 'Melhora significativa.',
      },
    })

    const wrapper = mount(SimulatorView, {
      global: { stubs: { AppLayout: AppLayoutStub } },
    })
    await flushPromises()

    wrapper.vm.selectedPropId = 1
    await wrapper.vm.onPropChange()
    await flushPromises()

    wrapper.vm.selectedAnalysisId = 10
    wrapper.vm.cultura = 'Soja'

    await wrapper.vm.simulate()
    await flushPromises()

    expect(wrapper.text()).toContain('40')
    expect(wrapper.text()).toContain('72')
  })

  it('shows error message on simulation failure', async () => {
    ;(api.get as any)
      .mockResolvedValueOnce({ data: [{ id: 1, nome: 'Fazenda A' }] })
      .mockResolvedValueOnce({
        data: [{ id: 10, id_amostra: 'AM-001', data_analise: '2024-01-15' }],
      })
    ;(api.post as any).mockRejectedValueOnce(new Error('fail'))

    const wrapper = mount(SimulatorView, {
      global: { stubs: { AppLayout: AppLayoutStub } },
    })
    await flushPromises()

    wrapper.vm.selectedPropId = 1
    await wrapper.vm.onPropChange()
    await flushPromises()

    wrapper.vm.selectedAnalysisId = 10
    wrapper.vm.cultura = 'Soja'

    await wrapper.vm.simulate()
    await flushPromises()

    expect(wrapper.text()).toContain('Erro')
  })
})
