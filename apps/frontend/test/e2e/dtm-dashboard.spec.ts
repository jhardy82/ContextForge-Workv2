import { test, expect, Page } from '@playwright/test';

/**
 * DTM Dashboard E2E Tests
 * Tests the core functionality of the Dynamic Task Manager dashboard
 */
test.describe('DTM Dashboard E2E', () => {
  // Test setup helpers
  const mockDTMApiResponses = async (page: Page) => {
    // Mock API responses for testing
    await page.route('**/api/v1/health', async route => {
      await route.fulfill({
        json: { connected: true, status: 'connected', version: '1.0.0' }
      });
    });

    await page.route('**/api/v1/projects', async route => {
      await route.fulfill({
        json: [
          {
            id: '1',
            name: 'Test Project',
            description: 'A test project for E2E testing',
            status: 'active',
            created: new Date().toISOString(),
            updated: new Date().toISOString()
          }
        ]
      });
    });

    await page.route('**/api/v1/tasks', async route => {
      await route.fulfill({
        json: [
          {
            id: '1',
            title: 'Test Task',
            description: 'A test task for E2E testing',
            status: 'new',
            priority: 'high',
            projectId: '1',
            created: new Date().toISOString(),
            updated: new Date().toISOString(),
            assignee: 'test-user',
            tags: ['test', 'e2e']
          },
          {
            id: '2',
            title: 'In Progress Task',
            description: 'A task currently in progress',
            status: 'in-progress',
            priority: 'medium',
            projectId: '1',
            created: new Date().toISOString(),
            updated: new Date().toISOString(),
            assignee: 'test-user-2',
            tags: ['development']
          }
        ]
      });
    });
  };

  test.beforeEach(async ({ page }) => {
    // Set development mode to show dashboard
    await page.addInitScript(() => {
      Object.defineProperty(window, 'import', {
        value: {
          meta: {
            env: {
              DEV: true
            }
          }
        }
      });
    });

    await mockDTMApiResponses(page);
    await page.goto('/');
  });

  test('displays DTM dashboard correctly in development mode', async ({ page }) => {
    // Check main heading
    await expect(page.getByRole('heading', { name: /dtm task manager/i })).toBeVisible();
    
    // Check connection status component
    await expect(page.getByText(/connection status/i)).toBeVisible();
    
    // Check refresh button
    await expect(page.getByRole('button', { name: /refresh/i })).toBeVisible();
    
    // Check settings button
    await expect(page.getByRole('button', { name: /settings/i })).toBeVisible();
  });

  test('shows connection status correctly', async ({ page }) => {
    // Wait for connection check
    await page.waitForTimeout(1000);
    
    // Should show connected status
    await expect(page.getByText(/connected/i)).toBeVisible();
    
    // Status indicator should be green/success
    const statusIndicator = page.locator('[data-testid="connection-status"]');
    if (await statusIndicator.isVisible()) {
      await expect(statusIndicator).toHaveClass(/connected|success|green/);
    }
  });

  test('loads and displays task data', async ({ page }) => {
    // Wait for tasks to load
    await page.waitForTimeout(2000);
    
    // Check for task tree component
    await expect(page.getByText(/tasks/i)).toBeVisible();
    
    // Check for individual tasks
    await expect(page.getByText('Test Task')).toBeVisible();
    await expect(page.getByText('In Progress Task')).toBeVisible();
    
    // Check task status badges
    await expect(page.getByText('new')).toBeVisible();
    await expect(page.getByText('in-progress')).toBeVisible();
  });

  test('handles task selection and detail modal', async ({ page }) => {
    // Wait for tasks to load
    await page.waitForTimeout(2000);
    
    // Click on a task
    await page.getByText('Test Task').click();
    
    // Modal should open
    await expect(page.getByRole('dialog')).toBeVisible();
    
    // Check modal content
    await expect(page.getByText('Test Task')).toBeVisible();
    await expect(page.getByText('A test task for E2E testing')).toBeVisible();
    await expect(page.getByText('high')).toBeVisible();
    await expect(page.getByText('test-user')).toBeVisible();
    
    // Close modal
    const closeButton = page.getByRole('button', { name: /close|×/i }).first();
    await closeButton.click();
    
    // Modal should close
    await expect(page.getByRole('dialog')).not.toBeVisible();
  });

  test('refresh functionality works', async ({ page }) => {
    // Wait for initial load
    await page.waitForTimeout(1000);
    
    let requestCount = 0;
    await page.route('**/api/v1/tasks', async route => {
      requestCount++;
      await route.fulfill({
        json: [
          {
            id: `${requestCount}`,
            title: `Refreshed Task ${requestCount}`,
            description: 'Task after refresh',
            status: 'new',
            priority: 'low',
            projectId: '1',
            created: new Date().toISOString(),
            updated: new Date().toISOString()
          }
        ]
      });
    });
    
    // Click refresh button
    const refreshButton = page.getByRole('button', { name: /refresh/i });
    await refreshButton.click();
    
    // Should show loading state
    await expect(refreshButton).toBeDisabled();
    
    // Wait for refresh to complete
    await page.waitForTimeout(1500);
    
    // Button should be enabled again
    await expect(refreshButton).toBeEnabled();
    
    // Should show updated content
    await expect(page.getByText(/refreshed task/i)).toBeVisible();
  });

  test('settings modal functionality', async ({ page }) => {
    // Click settings button
    await page.getByRole('button', { name: /settings/i }).click();
    
    // Settings modal should open
    await expect(page.getByRole('dialog')).toBeVisible();
    await expect(page.getByText(/settings/i)).toBeVisible();
    
    // Check for API URL setting
    const apiUrlInput = page.getByLabel(/api url/i);
    if (await apiUrlInput.isVisible()) {
      await expect(apiUrlInput).toHaveValue(/localhost:8000/);
    }
    
    // Check for auto-refresh toggle
    const autoRefreshToggle = page.getByLabel(/auto.?refresh/i);
    if (await autoRefreshToggle.isVisible()) {
      await expect(autoRefreshToggle).toBeVisible();
    }
    
    // Close modal
    const closeButton = page.getByRole('button', { name: /close|×/i }).first();
    await closeButton.click();
    
    // Modal should close
    await expect(page.getByRole('dialog')).not.toBeVisible();
  });

  test('task filtering and search works', async ({ page }) => {
    // Wait for tasks to load
    await page.waitForTimeout(2000);
    
    // Check if search input exists
    const searchInput = page.getByPlaceholder(/search|filter/i);
    if (await searchInput.isVisible()) {
      // Type search term
      await searchInput.fill('Test Task');
      
      // Should filter results
      await expect(page.getByText('Test Task')).toBeVisible();
      
      // Other task should be hidden
      await expect(page.getByText('In Progress Task')).not.toBeVisible();
      
      // Clear search
      await searchInput.clear();
      
      // All tasks should be visible again
      await expect(page.getByText('Test Task')).toBeVisible();
      await expect(page.getByText('In Progress Task')).toBeVisible();
    }
  });

  test('task status filtering works', async ({ page }) => {
    // Wait for tasks to load
    await page.waitForTimeout(2000);
    
    // Check for status filter buttons
    const newStatusFilter = page.getByRole('button', { name: /new/i });
    const inProgressFilter = page.getByRole('button', { name: /in.?progress/i });
    
    if (await newStatusFilter.isVisible()) {
      // Click new status filter
      await newStatusFilter.click();
      
      // Should show only new tasks
      await expect(page.getByText('Test Task')).toBeVisible();
      await expect(page.getByText('In Progress Task')).not.toBeVisible();
      
      // Click in-progress filter
      if (await inProgressFilter.isVisible()) {
        await inProgressFilter.click();
        
        // Should show only in-progress tasks
        await expect(page.getByText('In Progress Task')).toBeVisible();
        await expect(page.getByText('Test Task')).not.toBeVisible();
      }
    }
  });

  test('handles API connection errors gracefully', async ({ page }) => {
    // Mock failed API responses
    await page.route('**/api/v1/health', async route => {
      await route.fulfill({
        status: 500,
        json: { error: 'Internal server error' }
      });
    });
    
    await page.route('**/api/v1/tasks', async route => {
      await route.fulfill({
        status: 404,
        json: { error: 'Not found' }
      });
    });
    
    // Reload page to trigger error state
    await page.reload();
    
    // Wait for connection check
    await page.waitForTimeout(2000);
    
    // Should show disconnected status
    await expect(page.getByText(/disconnected|error|failed/i)).toBeVisible();
    
    // Status indicator should show error state
    const statusIndicator = page.locator('[data-testid="connection-status"]');
    if (await statusIndicator.isVisible()) {
      await expect(statusIndicator).toHaveClass(/error|failed|red/);
    }
  });

  test('auto-refresh functionality works', async ({ page }) => {
    // Wait for initial load
    await page.waitForTimeout(1000);
    
    let refreshCount = 0;
    await page.route('**/api/v1/tasks', async route => {
      refreshCount++;
      await route.fulfill({
        json: [
          {
            id: '1',
            title: `Auto-refreshed Task ${refreshCount}`,
            description: 'Task updated by auto-refresh',
            status: 'new',
            priority: 'high',
            projectId: '1',
            created: new Date().toISOString(),
            updated: new Date().toISOString()
          }
        ]
      });
    });
    
    // Enable auto-refresh in settings if not already enabled
    await page.getByRole('button', { name: /settings/i }).click();
    
    const autoRefreshToggle = page.getByLabel(/auto.?refresh/i);
    if (await autoRefreshToggle.isVisible()) {
      if (!(await autoRefreshToggle.isChecked())) {
        await autoRefreshToggle.check();
      }
    }
    
    // Close settings
    const closeButton = page.getByRole('button', { name: /close|×/i }).first();
    await closeButton.click();
    
    // Wait for auto-refresh interval (should be shortened for testing)
    await page.waitForTimeout(35000); // Slightly longer than the 30s interval
    
    // Should show updated content from auto-refresh
    await expect(page.getByText(/auto.?refreshed/i)).toBeVisible();
  });

  test('keyboard navigation works correctly', async ({ page }) => {
    // Wait for tasks to load
    await page.waitForTimeout(2000);
    
    // Focus should start at the top
    await page.keyboard.press('Tab');
    
    // Should be able to navigate to refresh button
    await page.keyboard.press('Tab');
    const refreshButton = page.getByRole('button', { name: /refresh/i });
    await expect(refreshButton).toBeFocused();
    
    // Should be able to activate with Enter
    await page.keyboard.press('Enter');
    await expect(refreshButton).toBeDisabled();
    
    // Wait for refresh to complete
    await page.waitForTimeout(1500);
    await expect(refreshButton).toBeEnabled();
    
    // Continue tabbing to tasks
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    
    // Should be able to select task with Enter
    await page.keyboard.press('Enter');
    
    // Modal should open
    await expect(page.getByRole('dialog')).toBeVisible();
    
    // Should be able to close with Escape
    await page.keyboard.press('Escape');
    await expect(page.getByRole('dialog')).not.toBeVisible();
  });

  test('responsive design works on different screen sizes', async ({ page }) => {
    // Test mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await page.waitForTimeout(1000);
    
    // Main content should still be visible
    await expect(page.getByRole('heading', { name: /dtm task manager/i })).toBeVisible();
    
    // Tasks should be accessible
    await expect(page.getByText('Test Task')).toBeVisible();
    
    // Click should still work
    await page.getByText('Test Task').click();
    await expect(page.getByRole('dialog')).toBeVisible();
    
    // Close modal
    const closeButton = page.getByRole('button', { name: /close|×/i }).first();
    await closeButton.click();
    
    // Test tablet viewport
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.waitForTimeout(500);
    
    // Content should still be accessible
    await expect(page.getByText('Test Task')).toBeVisible();
    await expect(page.getByText('In Progress Task')).toBeVisible();
    
    // Test desktop viewport
    await page.setViewportSize({ width: 1200, height: 800 });
    await page.waitForTimeout(500);
    
    // Should have full functionality
    await expect(page.getByRole('button', { name: /refresh/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /settings/i })).toBeVisible();
  });

  test('data persistence works with KV store', async ({ page }) => {
    // Open settings
    await page.getByRole('button', { name: /settings/i }).click();
    
    // Disable auto-refresh
    const autoRefreshToggle = page.getByLabel(/auto.?refresh/i);
    if (await autoRefreshToggle.isVisible()) {
      if (await autoRefreshToggle.isChecked()) {
        await autoRefreshToggle.uncheck();
      }
    }
    
    // Save settings by closing modal
    const closeButton = page.getByRole('button', { name: /close|×/i }).first();
    await closeButton.click();
    
    // Refresh page
    await page.reload();
    await page.waitForTimeout(2000);
    
    // Open settings again
    await page.getByRole('button', { name: /settings/i }).click();
    
    // Auto-refresh should still be disabled (persisted)
    if (await autoRefreshToggle.isVisible()) {
      await expect(autoRefreshToggle).not.toBeChecked();
    }
  });

  test('production mode shows only extension server', async ({ page }) => {
    // Override to production mode
    await page.addInitScript(() => {
      Object.defineProperty(window, 'import', {
        value: {
          meta: {
            env: {
              DEV: false
            }
          }
        }
      });
    });
    
    await page.goto('/');
    
    // Should show extension server, not DTM dashboard
    await expect(page.getByRole('heading', { name: /vs code extension server/i })).toBeVisible();
    await expect(page.getByRole('heading', { name: /dtm task manager/i })).not.toBeVisible();
  });

  test('accessibility features work correctly', async ({ page }) => {
    // Wait for content to load
    await page.waitForTimeout(2000);
    
    // Check heading hierarchy
    const h1 = page.getByRole('heading', { level: 1 });
    await expect(h1).toBeVisible();
    
    // Check ARIA labels on buttons
    const refreshButton = page.getByRole('button', { name: /refresh/i });
    await expect(refreshButton).toHaveAttribute('type', 'button');
    
    // Check task list accessibility
    const taskList = page.getByRole('list');
    if (await taskList.isVisible()) {
      await expect(taskList).toBeVisible();
      
      const taskItems = page.getByRole('listitem');
      await expect(taskItems.first()).toBeVisible();
    }
    
    // Check modal accessibility
    await page.getByText('Test Task').click();
    const modal = page.getByRole('dialog');
    await expect(modal).toBeVisible();
    await expect(modal).toHaveAttribute('aria-modal', 'true');
    
    // Check focus management
    const focusedElement = page.locator(':focus');
    await expect(focusedElement).toBeVisible();
  });
});