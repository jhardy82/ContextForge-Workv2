import { test, expect } from '@playwright/test';

/**
 * DTM Smoke Tests
 * Critical functionality tests that must pass for basic application health
 * These tests should be fast and cover the most important user journeys
 */
test.describe('DTM Smoke Tests @smoke', () => {
  test.beforeEach(async ({ page }) => {
    // Mock minimal API responses for smoke tests
    await page.route('**/api/v1/health', async route => {
      await route.fulfill({
        json: { version: '1.0.0', uptime: '1h' }
      });
    });

    await page.route('**/api/v1/projects', async route => {
      await route.fulfill({
        json: [
          {
            id: 'P-SMOKE-001',
            name: 'Smoke Test Project',
            description: 'Basic project for smoke testing',
            status: 'active',
            created_at: '2024-01-01T00:00:00Z'
          }
        ]
      });
    });

    await page.route('**/api/v1/tasks', async route => {
      await route.fulfill({
        json: [
          {
            id: 'T-SMOKE-001',
            title: 'Smoke Test Task',
            description: 'Basic task for smoke testing',
            status: 'new',
            priority: 'high',
            shape: 'Triangle',
            project_id: 'P-SMOKE-001',
            created_at: '2024-01-01T00:00:00Z'
          }
        ]
      });
    });

    // Set development mode for DTM dashboard
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
  });

  test('application loads successfully', async ({ page }) => {
    await page.goto('/');
    
    // Check that the main heading is visible
    await expect(page.getByRole('heading', { name: /dtm task manager/i })).toBeVisible();
    
    // Check that basic UI elements are present
    await expect(page.getByRole('button', { name: /refresh/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /settings/i })).toBeVisible();
  });

  test('API connection works', async ({ page }) => {
    await page.goto('/');
    
    // Wait for connection check
    await page.waitForTimeout(2000);
    
    // Should show connected status
    await expect(page.getByText(/connected/i)).toBeVisible();
  });

  test('task data loads and displays', async ({ page }) => {
    await page.goto('/');
    
    // Wait for data to load
    await page.waitForTimeout(2000);
    
    // Should display the smoke test task
    await expect(page.getByText('Smoke Test Task')).toBeVisible();
    
    // Should show task status
    await expect(page.getByText('new')).toBeVisible();
  });

  test('task modal opens and closes', async ({ page }) => {
    await page.goto('/');
    await page.waitForTimeout(2000);
    
    // Click on task to open modal
    await page.getByText('Smoke Test Task').click();
    
    // Modal should be visible
    await expect(page.getByRole('dialog')).toBeVisible();
    
    // Should show task details
    await expect(page.getByText('Smoke Test Task')).toBeVisible();
    
    // Close modal
    await page.keyboard.press('Escape');
    
    // Modal should be closed
    await expect(page.getByRole('dialog')).not.toBeVisible();
  });

  test('settings modal works', async ({ page }) => {
    await page.goto('/');
    await page.waitForTimeout(1000);
    
    // Open settings
    await page.getByRole('button', { name: /settings/i }).click();
    
    // Settings modal should be visible
    await expect(page.getByRole('dialog')).toBeVisible();
    
    // Close settings
    await page.keyboard.press('Escape');
    
    // Modal should be closed
    await expect(page.getByRole('dialog')).not.toBeVisible();
  });

  test('refresh functionality works', async ({ page }) => {
    await page.goto('/');
    await page.waitForTimeout(1000);
    
    // Click refresh button
    const refreshButton = page.getByRole('button', { name: /refresh/i });
    await refreshButton.click();
    
    // Button should briefly be disabled during refresh
    await expect(refreshButton).toBeDisabled();
    
    // Wait for refresh to complete
    await page.waitForTimeout(1000);
    
    // Button should be enabled again
    await expect(refreshButton).toBeEnabled();
  });

  test('keyboard navigation works', async ({ page }) => {
    await page.goto('/');
    await page.waitForTimeout(2000);
    
    // Tab navigation should work
    await page.keyboard.press('Tab');
    
    // Some element should be focused
    const focusedElement = page.locator(':focus');
    await expect(focusedElement).toBeVisible();
    
    // Continue tabbing
    await page.keyboard.press('Tab');
    await expect(page.locator(':focus')).toBeVisible();
  });

  test('responsive design works on mobile', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    await page.goto('/');
    await page.waitForTimeout(1000);
    
    // Main content should still be visible
    await expect(page.getByRole('heading', { name: /dtm task manager/i })).toBeVisible();
    
    // Task should be accessible
    await expect(page.getByText('Smoke Test Task')).toBeVisible();
  });

  test('production mode shows extension server', async ({ page }) => {
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
    
    // Should show extension server in production
    await expect(page.getByRole('heading', { name: /vs code extension server/i })).toBeVisible();
    
    // Should not show DTM dashboard
    await expect(page.getByRole('heading', { name: /dtm task manager/i })).not.toBeVisible();
  });

  test('error handling works', async ({ page }) => {
    // Mock API errors
    await page.route('**/api/v1/health', async route => {
      await route.fulfill({
        status: 500,
        json: { error: 'Server error' }
      });
    });
    
    await page.goto('/');
    await page.waitForTimeout(2000);
    
    // Should show disconnected/error state
    await expect(page.getByText(/disconnected|error|failed/i)).toBeVisible();
  });

  test('basic accessibility features work', async ({ page }) => {
    await page.goto('/');
    await page.waitForTimeout(2000);
    
    // Should have proper heading hierarchy
    const h1Elements = await page.locator('h1').count();
    expect(h1Elements).toBeGreaterThan(0);
    
    // Interactive elements should be keyboard accessible
    await page.keyboard.press('Tab');
    const focusedElement = page.locator(':focus');
    await expect(focusedElement).toBeVisible();
    
    // Should be able to activate with Enter
    await page.keyboard.press('Enter');
    // This might trigger an action - just verify no crash
  });

  test('page title is set correctly', async ({ page }) => {
    await page.goto('/');
    
    // Check page title
    await expect(page).toHaveTitle(/dtm task manager/i);
  });

  test('no JavaScript errors in console', async ({ page }) => {
    const errors: string[] = [];
    
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });
    
    page.on('pageerror', error => {
      errors.push(error.message);
    });
    
    await page.goto('/');
    await page.waitForTimeout(3000);
    
    // Perform basic interactions
    await page.getByText('Smoke Test Task').click();
    await page.keyboard.press('Escape');
    await page.getByRole('button', { name: /refresh/i }).click();
    await page.waitForTimeout(1000);
    
    // Filter out known harmless errors
    const significantErrors = errors.filter(error => 
      !error.includes('favicon') &&
      !error.includes('DevTools') &&
      !error.includes('Extension')
    );
    
    expect(significantErrors).toHaveLength(0);
  });

  test('basic performance is acceptable', async ({ page }) => {
    const startTime = Date.now();
    
    await page.goto('/');
    
    // Wait for main content
    await page.waitForSelector('h1');
    
    const loadTime = Date.now() - startTime;
    
    // Should load within 5 seconds (generous for smoke test)
    expect(loadTime).toBeLessThan(5000);
  });

  test('data persistence works', async ({ page }) => {
    await page.goto('/');
    
    // Open settings and make a change
    await page.getByRole('button', { name: /settings/i }).click();
    
    const autoRefreshToggle = page.getByLabel(/auto.?refresh/i);
    if (await autoRefreshToggle.isVisible()) {
      const initialState = await autoRefreshToggle.isChecked();
      
      // Toggle the setting
      if (initialState) {
        await autoRefreshToggle.uncheck();
      } else {
        await autoRefreshToggle.check();
      }
      
      // Close settings
      await page.keyboard.press('Escape');
      
      // Refresh page
      await page.reload();
      await page.waitForTimeout(1000);
      
      // Open settings again
      await page.getByRole('button', { name: /settings/i }).click();
      
      // Setting should be persisted
      if (await autoRefreshToggle.isVisible()) {
        const finalState = await autoRefreshToggle.isChecked();
        expect(finalState).toBe(!initialState);
      }
    }
  });

  test('extension server functionality (production mode)', async ({ page }) => {
    // Set production mode
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
    
    // Should show extension server
    await expect(page.getByRole('heading', { name: /vs code extension server/i })).toBeVisible();
    
    // Should show available extensions
    await expect(page.getByText('Available Extensions')).toBeVisible();
    
    // Should show sample extension
    await expect(page.getByText('VS Code TODOs')).toBeVisible();
  });
});