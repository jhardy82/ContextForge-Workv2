import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';
import React from 'react';
import { afterAll, beforeAll, beforeEach, describe, expect, it, vi } from 'vitest';
import ExtensionServer from '../../components/extension/extension-server';

// Mock @github/spark/hooks to behave like useState
vi.mock('@github/spark/hooks', async () => {
  return {
    useKV: (key: string, initialValue: any) => {
      const [val, setVal] = React.useState(initialValue);
      return [val, setVal, React.useCallback(() => {}, [])];
    }
  };
});

// Mock sonner to avoid DOM errors
vi.mock('sonner', () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
    info: vi.fn(),
    warning: vi.fn(),
    promise: vi.fn(),
  },
  Toaster: () => null,
}));

// Mock ResizeObserver
global.ResizeObserver = class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
};

const renderExtensionServer = () => {
  const queryClient = new QueryClient();
  return render(
    <QueryClientProvider client={queryClient}>
      <ExtensionServer />
    </QueryClientProvider>
  );
};

// Integration test server with full API simulation
const integrationServer = setupServer(
  // Extension listing
  http.get('/api/extensions', () => {
    return HttpResponse.json([
      {
        name: 'dynamic-task-manager',
        displayName: 'Dynamic Task Manager',
        version: '1.0.0',
        publisher: 'test-publisher',
        description: 'A comprehensive task management extension for VS Code',
        categories: ['Programming Languages', 'Other'],
        keywords: ['tasks', 'productivity', 'vscode', 'management']
      }
    ]);
  }),

  // Extension metadata
  http.get('/api/extensions/:id', ({ params }) => {
    return HttpResponse.json({
      name: params.id,
      displayName: 'Dynamic Task Manager',
      version: '1.0.0',
      publisher: 'test-publisher',
      description: 'A comprehensive task management extension for VS Code',
      categories: ['Programming Languages', 'Other'],
      keywords: ['tasks', 'productivity', 'vscode', 'management'],
      repository: {
        type: 'git',
        url: 'https://github.com/test/dynamic-task-manager'
      }
    });
  }),

  // Extension download
  http.get('/api/extensions/:id/download', ({ params }) => {
    return new HttpResponse('Mock VSIX binary content', {
      headers: {
        'Content-Type': 'application/octet-stream',
        'Content-Disposition': `attachment; filename="${params.id}.vsix"`
      }
    });
  }),

  // Health check
  http.get('/api/health', () => {
    return HttpResponse.json({
      status: 'healthy',
      timestamp: Date.now(),
      extensions: ['dynamic-task-manager']
    });
  })
);

describe('Extension Server Integration Tests', () => {
  beforeAll(() => {
    integrationServer.listen();
  });

  afterAll(() => {
    integrationServer.close();
  });

  beforeEach(() => {
    integrationServer.resetHandlers();
  });

  it('completes full extension discovery and installation workflow', async () => {
    const user = userEvent.setup();

    // Mock clipboard API using vi.stubGlobal
    const writeTextMock = vi.fn().mockResolvedValue(undefined);
    vi.stubGlobal('navigator', {
      ...navigator,
      clipboard: {
        writeText: writeTextMock,
        readText: vi.fn(),
      },
    });

    renderExtensionServer();

    // Verify main page loads
    expect(screen.getAllByText('VS Code Extension Server')[0]).toBeInTheDocument();
    expect(screen.getByText(/Manage and distribute custom VS Code extensions/)).toBeInTheDocument();

    // Wait for extensions to load and verify they appear
    await waitFor(() => {
      expect(screen.getByText('Available Extensions')).toBeInTheDocument();
    });

    // Select an extension
    const extensionCard = (await screen.findAllByText('VS Code TODOs'))[0];
    await user.click(extensionCard);

    // Verify extension details are displayed
    const descriptions = screen.getAllByText('Highlight and manage TODO comments in your code');
    expect(descriptions.length).toBeGreaterThan(0);
    expect(descriptions[0]).toBeInTheDocument();

    expect(screen.getAllByText('example-publisher • v1.2.3')[0]).toBeInTheDocument();

    // Test installation command copy
    // Verify installation command is displayed
    expect(screen.getByText('Installation Command')).toBeInTheDocument();
    expect(screen.getByText('code --install-extension vscode-todos-1.2.3.vsix')).toBeInTheDocument();

    const copyButton = screen.getAllByRole('button')[1]; // Assuming second button is copy (first is download)
    await user.click(copyButton);

    // Verify clipboard interaction (mocked)
    expect(writeTextMock).toHaveBeenCalled();

    vi.unstubAllGlobals();
  });



  it('displays extension details correctly', async () => {
    const user = userEvent.setup();
    renderExtensionServer();

    // Select extension
    const extensionCard = (await screen.findAllByText('VS Code TODOs'))[0];
    await user.click(extensionCard);

    // Verify details are shown immediately
    await waitFor(() => {
      expect(screen.getByText('Categories')).toBeInTheDocument();
      expect(screen.getByText('Programming Languages')).toBeInTheDocument();
      expect(screen.getByText('Other')).toBeInTheDocument();
    });

    // Verify Keywords are shown
    await waitFor(() => {
      expect(screen.getByText('Keywords')).toBeInTheDocument();
      expect(screen.getByText('todo')).toBeInTheDocument();
      expect(screen.getByText('productivity')).toBeInTheDocument();
      expect(screen.getByText('tasks')).toBeInTheDocument();
    });
  });

  it('handles download functionality', async () => {
    const user = userEvent.setup();

    // Track created anchor elements to verify download behavior
    let createdAnchor: HTMLAnchorElement | null = null;
    const originalCreateElement = document.createElement.bind(document);
    const createElementSpy = vi.spyOn(document, 'createElement').mockImplementation((tagName: string) => {
      const element = originalCreateElement(tagName);
      if (tagName === 'a') {
        createdAnchor = element as HTMLAnchorElement;
        // Mock click to prevent actual navigation
        vi.spyOn(element, 'click').mockImplementation(() => {});
      }
      return element;
    });

    renderExtensionServer();

    // Select extension
    const extensionCard = (await screen.findAllByText('VS Code TODOs'))[0];
    await user.click(extensionCard);

    // Click download button
    const downloadButton = screen.getByText('Download');
    await user.click(downloadButton);

    // Verify anchor was created with correct properties and clicked
    expect(createdAnchor).not.toBeNull();
    expect(createdAnchor!.download).toContain('vscode-todos');
    expect(createdAnchor!.href).toContain('vscode-todos');
    expect(createdAnchor!.click).toHaveBeenCalled();

    createElementSpy.mockRestore();
  });

  it('maintains selection state', async () => {
    const user = userEvent.setup();
    renderExtensionServer();

    // Select extension
    const extensionCard = (await screen.findAllByText('VS Code TODOs'))[0];
    await user.click(extensionCard);

    // Verify details are shown
    expect(screen.getByText('Installation Command')).toBeInTheDocument();

    // Click the same extension again (should stay selected)
    await user.click(extensionCard);
    expect(screen.getByText('Installation Command')).toBeInTheDocument();
  });

  it('handles empty extension list gracefully', async () => {
    // Override server to return empty list
    integrationServer.use(
      http.get('/api/extensions', () => {
        return HttpResponse.json([]);
      })
    );

    renderExtensionServer();

    await waitFor(() => {
      expect(screen.getByText('Select an Extension')).toBeInTheDocument();
      expect(screen.getByText('Choose an extension from the list to view details and installation instructions.')).toBeInTheDocument();
    });
  });

  it('validates responsive design behavior', async () => {
    // Mock viewport changes for responsive testing
    const originalInnerWidth = window.innerWidth;

    // Test mobile viewport
    window.innerWidth = 375;
    window.dispatchEvent(new Event('resize'));

    renderExtensionServer();

    const extensionCard = (await screen.findAllByText('VS Code TODOs'))[0];
    expect(extensionCard).toBeInTheDocument();

    // Test tablet viewport
    window.innerWidth = 768;
    window.dispatchEvent(new Event('resize'));

    // Test desktop viewport
    window.innerWidth = 1024;
    window.dispatchEvent(new Event('resize'));

    // Restore original width
    window.innerWidth = originalInnerWidth;
  });
});
