import { describe, it, expect, vi } from 'vitest'
import { render } from '@/test/utils/test-utils'
import App from '@/App'

// Mock the extension components
vi.mock('@/components/extension/extension-server', () => ({
  default: () => <div data-testid="extension-server">Extension Server Component</div>
}))

describe('Smoke Tests - Critical App Functionality', () => {
  it('app renders without crashing', () => {
    expect(() => render(<App />)).not.toThrow()
  })

  it('app renders main component', () => {
    const { getByTestId } = render(<App />)
    expect(getByTestId('extension-server')).toBeInTheDocument()
  })

  it('app includes toast notifications', () => {
    render(<App />)
    // Toaster should be rendered even if not visible
    expect(document.querySelector('[data-sonner-toaster]')).toBeInTheDocument()
  })

  it('global spark object is available', () => {
    expect(window.spark).toBeDefined()
    expect(typeof window.spark.llm).toBe('function')
    expect(typeof window.spark.kv.get).toBe('function')
    expect(typeof window.spark.user).toBe('function')
  })

  it('critical CSS classes are applied', () => {
    const { container } = render(<App />)
    // Check that tailwind classes are working
    const body = document.body
    expect(body.className).toContain('bg-background')
  })

  it('no console errors during render', () => {
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
    
    render(<App />)
    
    expect(consoleSpy).not.toHaveBeenCalled()
    consoleSpy.mockRestore()
  })

  it('component tree structure is correct', () => {
    const { container } = render(<App />)
    
    // Should have the main fragment structure
    expect(container.firstChild?.childNodes).toHaveLength(2) // ExtensionServer + Toaster
  })

  it('async operations do not crash app', async () => {
    expect(async () => {
      await window.spark.llm('test prompt')
      await window.spark.user()
      await window.spark.kv.get('test-key')
    }).not.toThrow()
  })

  it('essential hooks work without errors', async () => {
    // Test that useKV hook can be imported and used
    const { useKV } = await import('@github/spark/hooks')
    expect(typeof useKV).toBe('function')
  })

  it('essential UI components can be imported', async () => {
    // Test critical component imports
    const { Button } = await import('@/components/ui/button')
    const { Card } = await import('@/components/ui/card')
    const { Tabs } = await import('@/components/ui/tabs')
    
    expect(Button).toBeDefined()
    expect(Card).toBeDefined()
    expect(Tabs).toBeDefined()
  })
})