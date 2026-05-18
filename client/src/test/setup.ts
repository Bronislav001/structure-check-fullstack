import '@testing-library/jest-dom/vitest'

const originalWarn = console.warn.bind(console)

beforeAll(() => {
  vi.spyOn(console, 'warn').mockImplementation((...args: unknown[]) => {
    const first = String(args[0] ?? '')
    if (first.includes('React Router Future Flag Warning')) return
    originalWarn(...args)
  })
})

afterAll(() => {
  vi.restoreAllMocks()
})
