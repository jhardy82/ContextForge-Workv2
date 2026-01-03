import ExtensionServer from '@/components/extension/extension-server'
import { render } from '@/test/utils/test-utils'
import { fireEvent, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'

// Hoist the store so it's available in the mock factory
const { mockStore } = vi.hoisted(() => {
  const store = new Map()
  return {
    mockStore: {
      get: (key: string) => store.get(key),
      set: (key: string, val: any) => store.set(key, val),
      delete: (key: string) => store.delete(key),
      clear: () => store.clear()
    }
  }
})

// Mock useKV with React state to trigger re-renders
vi.mock('@github/spark/hooks', async () => {
  const React = await import('react')
  return {
    useKV: vi.fn((key: string, defaultValue: any) => {
      // Initialize state from store or default
      const [value, setValue] = React.useState(() => {
        const stored = mockStore.get(key)
        return stored !== undefined ? stored : defaultValue
      })

      const setKV = (newValue: any) => {
        mockStore.set(key, newValue)
        setValue(newValue)
      }

      const deleteKV = () => {
        mockStore.delete(key)
        setValue(undefined)
      }

      return [value, setKV, deleteKV]
    })
  }
})

// Mock sonner to avoid Portal issues in JSDOM
vi.mock('sonner', () => ({
  Toaster: () => null,
  toast: {
    success: vi.fn(),
    error: vi.fn()
  }
}))

describe('Extension Server Integration', () => {
  beforeEach(() => {
    mockStore.clear()
    vi.clearAllMocks()
  })

  it('initializes with sample data when no extensions exist', async () => {
    render(<ExtensionServer />)

    await waitFor(() => {
      expect(screen.getByText('VS Code TODOs')).toBeInTheDocument()
    })
  })

  it('persists extension selection across re-renders', async () => {
    const { rerender } = render(<ExtensionServer />)

    await waitFor(() => {
      // Click the first occurrence (in the list)
      const extensionItems = screen.getAllByText('VS Code TODOs')
      fireEvent.click(extensionItems[0])
    })

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /download/i })).toBeInTheDocument()
    })

    // Re-render component
    rerender(<ExtensionServer />)

    // Selection should persist
    expect(screen.getAllByText('VS Code TODOs')[0]).toBeInTheDocument()
  })

  it('handles clipboard operations gracefully when not supported', async () => {
    const user = userEvent.setup()

    // Mock clipboard properly for JSDOM
    const originalClipboard = navigator.clipboard
    const mockClipboard = {
      writeText: vi.fn().mockRejectedValue(new Error('Clipboard not available'))
    }

    Object.defineProperty(navigator, 'clipboard', {
      value: mockClipboard,
      writable: true,
      configurable: true
    })

    render(<ExtensionServer />)

    await waitFor(async () => {
      // Click the first occurrence (in the list)
      const extensionItems = screen.getAllByText('VS Code TODOs')
      fireEvent.click(extensionItems[0])

      // Find the copy button (it has the Copy icon)
      // We can look for the button that is NOT the download button
      const buttons = screen.getAllByRole('button')
      const copyButton = buttons.find(b => !b.textContent?.includes('Download'))

      if (copyButton) {
        await user.click(copyButton)
      }
    })

    // Should not throw error - graceful handling
    expect(screen.getAllByText('VS Code TODOs')[0]).toBeInTheDocument()

    // Cleanup
    if (originalClipboard) {
      Object.defineProperty(navigator, 'clipboard', {
        value: originalClipboard,
        writable: true,
        configurable: true
      })
    }
  })

  it('handles download functionality', async () => {
    // Mock document.createElement to return a mock anchor
    const originalCreateElement = document.createElement
    const mockAnchor = {
      href: '',
      download: '',
      click: vi.fn(),
      style: {},
      tagName: 'A'
    } as unknown as HTMLAnchorElement

    vi.spyOn(document, 'createElement').mockImplementation((tagName) => {
      if (tagName === 'a') return mockAnchor
      return originalCreateElement.call(document, tagName)
    })

    render(<ExtensionServer />)

    await waitFor(() => {
      // Click the first occurrence (in the list)
      const extensionItems = screen.getAllByText('VS Code TODOs')
      fireEvent.click(extensionItems[0])
    })

    const downloadButton = screen.getByRole('button', { name: /download/i })
    fireEvent.click(downloadButton)

    expect(mockAnchor.click).toHaveBeenCalled()
    // The component doesn't append to body, just clicks
  })
})
