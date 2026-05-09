import { describe, it, expect, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { defineComponent, Suspense } from 'vue'

vi.mock('munsell', () => ({
  munsellToRgb255: (code: string): [number, number, number] => {
    if (code === '10YR 3/2') return [87, 59, 38]
    if (code === '10YR 6/4') return [188, 152, 106]
    throw new Error('invalid munsell')
  },
}))

import SoilCoreViz from '@/components/SoilCoreViz.vue'

function mountWithSuspense(analyses: any[]) {
  const Wrapper = defineComponent({
    components: { SoilCoreViz },
    template: `<Suspense><SoilCoreViz :analyses="analyses" /></Suspense>`,
    setup() { return { analyses } },
  })
  return mount(Wrapper)
}

describe('SoilCoreViz', () => {
  it('renders one layer per analysis', async () => {
    const wrapper = mountWithSuspense([
      { id: 1, data_analise: '2024-01-15', materia_organica: 3.2, cor_munsell: '10YR 3/2' },
      { id: 2, data_analise: '2024-06-01', materia_organica: 2.1, cor_munsell: '10YR 6/4' },
    ])
    await flushPromises()
    expect(wrapper.findAll('.profile-layer').length).toBe(2)
  })

  it('valid Munsell color sets background-color', async () => {
    const wrapper = mountWithSuspense([
      { id: 1, data_analise: '2024-01-15', materia_organica: 3.2, cor_munsell: '10YR 3/2' },
    ])
    await flushPromises()
    const layer = wrapper.find('.profile-layer')
    const bg = layer.attributes('style') || ''
    expect(bg).toContain('87')
  })

  it('null cor_munsell falls back to default brown', async () => {
    const wrapper = mountWithSuspense([
      { id: 1, data_analise: '2024-01-15', materia_organica: 3.2, cor_munsell: null },
    ])
    await flushPromises()
    const layer = wrapper.find('.profile-layer')
    const bg = layer.attributes('style') || ''
    expect(bg).toContain('rgb(139, 115, 85)')
  })

  it('invalid Munsell string falls back to default brown', async () => {
    const wrapper = mountWithSuspense([
      { id: 1, data_analise: '2024-01-15', materia_organica: 3.2, cor_munsell: 'INVALID' },
    ])
    await flushPromises()
    const layer = wrapper.find('.profile-layer')
    const bg = layer.attributes('style') || ''
    expect(bg).toContain('rgb(139, 115, 85)')
  })
})
