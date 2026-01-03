import React, { ReactElement } from 'react'
import { render, RenderOptions } from '@testing-library/react'
import { expect } from 'vitest'
import { Toaster } from 'sonner'

// Custom render function that includes providers
const AllTheProviders = ({ children }: { children: React.ReactNode }) => {
  return (
    <div data-testid="test-providers-wrapper">
      {children}
      <Toaster />
    </div>
  )
}

const customRender = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => render(ui, { wrapper: AllTheProviders, ...options })

// Re-export everything
export * from '@testing-library/react'
export { customRender as render }

// Common test data generators
export const mockExtensionData = {
  info: {
    name: 'test-extension',
    displayName: 'Test Extension',
    description: 'A test extension for testing',
    version: '1.0.0',
    publisher: 'test-publisher',
    categories: ['Testing', 'Development'],
    keywords: ['test', 'mock', 'development']
  },
  downloadUrl: 'http://localhost/test-extension.vsix',
  installCommand: 'code --install-extension test-extension.vsix',
  metadata: '{"name": "test-extension"}',
  apiEndpoints: {
    metadata: 'http://localhost/api/extensions/test-extension',
    download: 'http://localhost/api/extensions/test-extension/download'
  }
}

// Mock KV store for testing
export const createMockKVStore = () => {
  const store = new Map()

  return {
    get: async (key: string) => store.get(key),
    set: async (key: string, value: any) => { store.set(key, value) },
    delete: async (key: string) => { store.delete(key) },
    keys: async () => Array.from(store.keys()),
    clear: () => { store.clear() }
  }
}

// Wait for loading states
export const waitForLoadingToFinish = () => {
  return new Promise(resolve => setTimeout(resolve, 0))
}

// Common assertions
export const expectElementToBeVisible = (element: HTMLElement) => {
  expect(element).toBeInTheDocument()
  expect(element).toBeVisible()
}

export const expectElementToHaveText = (element: HTMLElement, text: string) => {
  expect(element).toBeInTheDocument()
  expect(element).toHaveTextContent(text)
}
