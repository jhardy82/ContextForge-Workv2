import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { setupServer } from 'msw/node';
import { http, HttpResponse } from 'msw';
import App from '../../App';

// Smoke test server - minimal but realistic responses
const smokeTestServer = setupServer(
  http.get('/api/health', () => {
    return HttpResponse.json({ status: 'healthy' });
  }),

  http.get('/api/extensions', () => {
    return HttpResponse.json([
      {
        name: 'dynamic-task-manager',
        displayName: 'Dynamic Task Manager',
        version: '1.0.0',
        publisher: 'test-publisher',
        description: 'Task management for VS Code'
      }
    ]);
  })
);

describe('Smoke Tests - Critical Application Paths', () => {
  beforeAll(() => {
    smokeTestServer.listen();
  });

  afterAll(() => {
    smokeTestServer.close();
  });

  it('application loads without crashing', () => {
    expect(() => render(<App />)).not.toThrow();
  });

  it('displays main heading and navigation elements', async () => {
    render(<App />);
    
    expect(screen.getByText('VS Code Extension Server')).toBeInTheDocument();
    expect(screen.getByText(/Manage and distribute custom VS Code extensions/)).toBeInTheDocument();
    
    // Wait for extension list to load
    await waitFor(() => {
      expect(screen.getByText('Available Extensions')).toBeInTheDocument();
    }, { timeout: 5000 });
  });

  it('extension list loads and displays extensions', async () => {
    render(<App />);
    
    // Wait for extensions to load from server
    await waitFor(() => {
      expect(screen.getByText('Dynamic Task Manager')).toBeInTheDocument();
    }, { timeout: 5000 });
    
    expect(screen.getByText('test-publisher • v1.0.0')).toBeInTheDocument();
  });

  it('extension selection shows details panel', async () => {
    const user = userEvent.setup();
    render(<App />);
    
    // Wait for extension to be available
    const extensionItem = await screen.findByText('Dynamic Task Manager');
    
    // Select extension
    await user.click(extensionItem);
    
    // Verify details panel appears
    await waitFor(() => {
      expect(screen.getByText('Download')).toBeInTheDocument();
    });
    
    expect(screen.getByText('Installation Command')).toBeInTheDocument();
  });

  it('critical UI components render without errors', async () => {
    render(<App />);
    
    // Verify core UI elements exist
    expect(screen.getByText('VS Code Extension Server')).toBeInTheDocument();
    
    // Wait for main content to load
    await waitFor(() => {
      expect(screen.getByText('Available Extensions')).toBeInTheDocument();
    });
    
    // Verify that tabs are present (even if not selected)
    const extensionItem = await screen.findByText('Dynamic Task Manager');
    await userEvent.setup().click(extensionItem);
    
    expect(screen.getByText('Install')).toBeInTheDocument();
    expect(screen.getByText('API')).toBeInTheDocument();
    expect(screen.getByText('Details')).toBeInTheDocument();
    expect(screen.getByText('Keywords')).toBeInTheDocument();
  });

  it('clipboard functionality is available', async () => {
    const user = userEvent.setup();
    render(<App />);
    
    // Select extension first
    const extensionItem = await screen.findByText('Dynamic Task Manager');
    await user.click(extensionItem);
    
    // Find and click copy button
    const copyButtons = screen.getAllByRole('button', { name: /copy/i });
    expect(copyButtons.length).toBeGreaterThan(0);
    
    // Ensure clipboard API is mocked and functional
    await user.click(copyButtons[0]);
    expect(navigator.clipboard.writeText).toHaveBeenCalled();
  });

  it('page structure and accessibility basics', () => {
    render(<App />);
    
    // Check for proper heading hierarchy
    const mainHeading = screen.getByRole('heading', { level: 1 });
    expect(mainHeading).toHaveTextContent('VS Code Extension Server');
    
    // Check for buttons
    const buttons = screen.getAllByRole('button');
    expect(buttons.length).toBeGreaterThan(0);
    
    // Check for basic navigation elements
    expect(screen.getByText('Available Extensions')).toBeInTheDocument();
  });

  it('handles network errors gracefully', async () => {
    // Override server to simulate network error
    smokeTestServer.use(
      http.get('/api/extensions', () => {
        return HttpResponse.error();
      })
    );
    
    // App should still render even if API calls fail
    expect(() => render(<App />)).not.toThrow();
    
    expect(screen.getByText('VS Code Extension Server')).toBeInTheDocument();
  });

  it('essential state management works', async () => {
    const user = userEvent.setup();
    render(<App />);
    
    // Test that selection state is maintained
    const extensionItem = await screen.findByText('Dynamic Task Manager');
    await user.click(extensionItem);
    
    // Verify selection persisted by checking details are shown
    await waitFor(() => {
      expect(screen.getByText('Download')).toBeInTheDocument();
    });
    
    // Switch tabs to test tab state
    const apiTab = screen.getByText('API');
    await user.click(apiTab);
    
    await waitFor(() => {
      expect(screen.getByText('cURL Examples')).toBeInTheDocument();
    });
    
    // Switch back to install tab
    const installTab = screen.getByText('Install');
    await user.click(installTab);
    
    await waitFor(() => {
      expect(screen.getByText('Installation Command')).toBeInTheDocument();
    });
  });

  it('performance - initial render completes quickly', async () => {
    const startTime = performance.now();
    
    render(<App />);
    
    // Wait for main content to be visible
    await waitFor(() => {
      expect(screen.getByText('VS Code Extension Server')).toBeInTheDocument();
    });
    
    const endTime = performance.now();
    const renderTime = endTime - startTime;
    
    // Initial render should complete within 2 seconds
    expect(renderTime).toBeLessThan(2000);
  });

  it('no console errors during basic usage', async () => {
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    const user = userEvent.setup();
    
    render(<App />);
    
    // Perform basic interactions
    const extensionItem = await screen.findByText('Dynamic Task Manager');
    await user.click(extensionItem);
    
    // Switch between tabs
    await user.click(screen.getByText('API'));
    await user.click(screen.getByText('Details'));
    await user.click(screen.getByText('Install'));
    
    // Verify no console errors occurred
    expect(console.error).not.toHaveBeenCalled();
    
    consoleSpy.mockRestore();
  });
});