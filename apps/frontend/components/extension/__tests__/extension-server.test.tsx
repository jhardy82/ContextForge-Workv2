import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { render, mockExtensionData } from '@/test/utils/test-utils'
import ExtensionServer from '../extension-server'

// Mock the useKV hook
const mockSetExtensions = vi.fn()
vi.mock('@github/spark/hooks', () => ({
  useKV: vi.fn(() => [[], mockSetExtensions, vi.fn()])
}))

// Mock the api-server module
vi.mock('../api-server', () => ({
  useApiServer: vi.fn(() => ({})),
  generateCurlExamples: vi.fn(() => ({
    listExtensions: 'curl http://localhost/api/extensions',
    getExtension: 'curl http://localhost/api/extensions/test',
    downloadExtension: 'curl -O http://localhost/api/extensions/test/download'
  }))
}))

describe('ExtensionServer', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders the main heading', () => {
    render(<ExtensionServer />)

    expect(screen.getByRole('heading', { name: /vs code extension server/i })).toBeInTheDocument()
  })

  it('displays no extensions message when list is empty', () => {
    render(<ExtensionServer />)

    expect(screen.getByText('No extensions available')).toBeInTheDocument()
  })

  it('displays extension list when extensions are provided', async () => {
    const { useKV } = await import('@github/spark/hooks')
    vi.mocked(useKV).mockReturnValue([[mockExtensionData], mockSetExtensions, vi.fn()])

    render(<ExtensionServer />)

    expect(screen.getByText('Test Extension')).toBeInTheDocument()
    expect(screen.getByText('test-publisher • v1.0.0')).toBeInTheDocument()
  })

  it('selects extension when clicked', async () => {
    const { useKV } = await import('@github/spark/hooks')
    vi.mocked(useKV).mockReturnValue([[mockExtensionData], mockSetExtensions, vi.fn()])

    render(<ExtensionServer />)

    const extensionItem = screen.getByText('Test Extension')
    fireEvent.click(extensionItem)

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /download/i })).toBeInTheDocument()
    })
  })

  it('displays installation command when extension is selected', async () => {
    const { useKV } = await import('@github/spark/hooks')
    vi.mocked(useKV).mockReturnValue([[mockExtensionData], mockSetExtensions, vi.fn()])

    render(<ExtensionServer />)

    const extensionItem = screen.getByText('Test Extension')
    fireEvent.click(extensionItem)

    await waitFor(() => {
      expect(screen.getByText('code --install-extension test-extension.vsix')).toBeInTheDocument()
    })
  })

  it('copies install command to clipboard when copy button is clicked', async () => {
    const user = userEvent.setup()
    const { useKV } = await import('@github/spark/hooks')
    vi.mocked(useKV).mockReturnValue([[mockExtensionData], mockSetExtensions, vi.fn()])

    // Mock clipboard API
    const writeTextMock = vi.fn()
    vi.stubGlobal('navigator', {
      ...navigator,
      clipboard: {
        writeText: writeTextMock
      }
    })

    render(<ExtensionServer />)

    const extensionItem = screen.getByText('Test Extension')
    fireEvent.click(extensionItem)

    await waitFor(() => {
      const copyButton = screen.getAllByRole('button')[1] // Second button is copy
      return user.click(copyButton)
    })

    expect(writeTextMock).toHaveBeenCalledWith('code --install-extension test-extension.vsix')
  })

  it('displays extension categories', async () => {
    const { useKV } = await import('@github/spark/hooks')
    vi.mocked(useKV).mockReturnValue([[mockExtensionData], mockSetExtensions, vi.fn()])

    render(<ExtensionServer />)

    const extensionItem = screen.getByText('Test Extension')
    fireEvent.click(extensionItem)

    await waitFor(() => {
      expect(screen.getByText('Testing')).toBeInTheDocument()
      expect(screen.getByText('Development')).toBeInTheDocument()
    })
  })

  it('displays extension keywords', async () => {
    const { useKV } = await import('@github/spark/hooks')
    vi.mocked(useKV).mockReturnValue([[mockExtensionData], mockSetExtensions, vi.fn()])

    render(<ExtensionServer />)

    const extensionItem = screen.getByText('Test Extension')
    fireEvent.click(extensionItem)

    await waitFor(() => {
      expect(screen.getByText('test')).toBeInTheDocument()
      expect(screen.getByText('mock')).toBeInTheDocument()
      expect(screen.getByText('development')).toBeInTheDocument()
    })
  })

  it('shows install command', async () => {
    const { useKV } = await import('@github/spark/hooks')
    vi.mocked(useKV).mockReturnValue([[mockExtensionData], mockSetExtensions, vi.fn()])

    render(<ExtensionServer />)

    const extensionItem = screen.getByText('Test Extension')
    fireEvent.click(extensionItem)

    await waitFor(() => {
      expect(screen.getByText('code --install-extension test-extension.vsix')).toBeInTheDocument()
    })
  })
})
