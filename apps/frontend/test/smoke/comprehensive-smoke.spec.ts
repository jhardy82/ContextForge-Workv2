import { test, expect } from '@playwright/test';

/**
 * Comprehensive Smoke Testing Suite
 * Fast critical path validation to ensure core functionality works
 * before running more extensive test suites
 */
test.describe('Comprehensive Smoke Tests', () => {
  
  test.beforeEach(async ({ page }) => {
    // Setup minimal mock API responses for smoke testing
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
            name: 'Smoke Test Project',
            description: 'Quick validation project',
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
            title: 'Smoke Test Task',
            description: 'Critical path validation task',
            status: 'new',
            priority: 'high',
            projectId: '1',
            created: new Date().toISOString(),
            updated: new Date().toISOString(),
            assignee: 'smoke-tester',
            tags: ['smoke', 'critical']
          }
        ]
      });
    });

    // Set development mode to show DTM dashboard
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
    const startTime = Date.now();
    
    await page.goto('/');
    await page.waitForLoadState('domcontentloaded');
    
    const endTime = Date.now();
    const loadTime = endTime - startTime;
    
    // Should load quickly (< 5 seconds)
    expect(loadTime).toBeLessThan(5000);
    
    // Basic page structure should be present
    expect(await page.locator('body').isVisible()).toBe(true);
    expect(await page.locator('html').getAttribute('lang')).toBeTruthy();
    
    // Should not have any console errors
    const errors: string[] = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });
    
    await page.waitForTimeout(2000);
    
    // Filter out expected/harmless errors
    const criticalErrors = errors.filter(error => 
      !error.includes('favicon') && 
      !error.includes('404') && 
      !error.includes('chrome-extension') &&
      !error.includes('Non-Error promise rejection')
    );
    
    expect(criticalErrors).toHaveLength(0);
  });

  test('main navigation and UI elements render', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
    
    // Main heading should be visible
    const mainHeading = page.getByRole('heading', { level: 1 });
    await expect(mainHeading).toBeVisible();
    await expect(mainHeading).toContainText(/dtm|task|manager/i);
    
    // Essential navigation elements should be present
    const refreshButton = page.getByRole('button', { name: /refresh/i });
    const settingsButton = page.getByRole('button', { name: /settings/i });
    
    if (await refreshButton.isVisible()) {
      expect(await refreshButton.isEnabled()).toBe(true);
    }
    
    if (await settingsButton.isVisible()) {
      expect(await settingsButton.isEnabled()).toBe(true);
    }
  });

  test('API connectivity works', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // Connection status should show connected
    const statusIndicators = [
      'connected',
      'success',
      'online',
      'active'
    ];
    
    let connectionFound = false;
    for (const indicator of statusIndicators) {
      const element = page.getByText(new RegExp(indicator, 'i'));
      if (await element.isVisible()) {
        connectionFound = true;
        break;
      }
    }
    
    // Should have some indication of successful connection
    expect(connectionFound).toBe(true);
  });

  test('data loading and display works', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // Should display task data
    const taskText = page.getByText('Smoke Test Task');
    await expect(taskText).toBeVisible();
    
    // Should show task status
    const statusText = page.getByText('new');
    await expect(statusText).toBeVisible();
    
    // Should show some form of task list or container
    const taskContainer = page.locator('[data-testid*="task"], .task, .tasks, [class*="task"]').first();
    await expect(taskContainer).toBeVisible();
  });

  test('basic user interactions work', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // Test clicking on a task
    const taskElement = page.getByText('Smoke Test Task').first();
    if (await taskElement.isVisible()) {
      await taskElement.click();
      
      // Modal or detail view should appear
      const modal = page.getByRole('dialog');
      if (await modal.isVisible()) {
        // Should show task details
        await expect(modal).toContainText('Smoke Test Task');
        
        // Should be able to close modal
        await page.keyboard.press('Escape');
        await expect(modal).not.toBeVisible();
      }
    }
    
    // Test refresh functionality
    const refreshButton = page.getByRole('button', { name: /refresh/i });
    if (await refreshButton.isVisible()) {
      await refreshButton.click();
      
      // Button should become disabled temporarily
      await expect(refreshButton).toBeDisabled();
      
      // Wait for refresh to complete
      await page.waitForTimeout(1500);
      
      // Button should be enabled again
      await expect(refreshButton).toBeEnabled();
    }
  });

  test('responsive layout basics work', async ({ page }) => {
    // Test desktop layout
    await page.setViewportSize({ width: 1280, height: 720 });
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
    
    // Main content should be visible
    await expect(page.getByRole('heading', { level: 1 })).toBeVisible();
    
    // Test tablet layout
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.waitForTimeout(500);
    
    // Content should still be accessible
    await expect(page.getByRole('heading', { level: 1 })).toBeVisible();
    
    // Test mobile layout
    await page.setViewportSize({ width: 375, height: 667 });
    await page.waitForTimeout(500);
    
    // Essential elements should still be present
    await expect(page.getByRole('heading', { level: 1 })).toBeVisible();
    
    // Task should still be clickable
    const taskElement = page.getByText('Smoke Test Task').first();
    if (await taskElement.isVisible()) {
      await taskElement.click();
      
      const modal = page.getByRole('dialog');
      if (await modal.isVisible()) {
        await page.keyboard.press('Escape');
      }
    }
  });

  test('error handling works', async ({ page }) => {
    // Mock API error responses
    await page.route('**/api/v1/health', async route => {
      await route.fulfill({
        status: 500,
        json: { error: 'Server error' }
      });
    });
    
    await page.route('**/api/v1/tasks', async route => {
      await route.fulfill({
        status: 404,
        json: { error: 'Not found' }
      });
    });
    
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(3000);
    
    // Should handle errors gracefully without crashing
    expect(await page.locator('body').isVisible()).toBe(true);
    
    // Should show some indication of error state
    const errorIndicators = [
      'error',
      'failed',
      'disconnected',
      'unavailable',
      'problem'
    ];
    
    let errorFound = false;
    for (const indicator of errorIndicators) {
      const element = page.getByText(new RegExp(indicator, 'i'));
      if (await element.isVisible()) {
        errorFound = true;
        break;
      }
    }
    
    // Should indicate error state
    expect(errorFound).toBe(true);
  });

  test('keyboard navigation basics work', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // Tab navigation should work
    await page.keyboard.press('Tab');
    
    let focused = await page.locator(':focus').first();
    await expect(focused).toBeVisible();
    
    // Continue tabbing
    await page.keyboard.press('Tab');
    
    const newFocused = await page.locator(':focus').first();
    await expect(newFocused).toBeVisible();
    
    // Enter key should activate focused element
    if (await newFocused.evaluate(el => el.tagName.toLowerCase()) === 'button') {
      await page.keyboard.press('Enter');
      // Should not crash
      await page.waitForTimeout(500);
      expect(await page.locator('body').isVisible()).toBe(true);
    }
  });

  test('production mode works', async ({ page }) => {
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
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // Should show extension server interface
    const extensionHeading = page.getByRole('heading', { name: /vs code|extension|server/i });
    await expect(extensionHeading).toBeVisible();
    
    // Should not show DTM dashboard
    const dtmHeading = page.getByRole('heading', { name: /dtm task manager/i });
    await expect(dtmHeading).not.toBeVisible();
    
    // Extension list should be visible
    const extensionList = page.getByText(/available extensions|extensions/i);
    await expect(extensionList).toBeVisible();
  });

  test('performance is acceptable', async ({ page }) => {
    const startTime = Date.now();
    
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    const endTime = Date.now();
    const totalLoadTime = endTime - startTime;
    
    // Should load within reasonable time (< 10 seconds for smoke test)
    expect(totalLoadTime).toBeLessThan(10000);
    
    // Page should be interactive
    await page.waitForTimeout(1000);
    
    const interactionStart = Date.now();
    const refreshButton = page.getByRole('button', { name: /refresh/i });
    
    if (await refreshButton.isVisible()) {
      await refreshButton.click();
    }
    
    const interactionEnd = Date.now();
    const interactionTime = interactionEnd - interactionStart;
    
    // Interactions should be responsive (< 1 second)
    expect(interactionTime).toBeLessThan(1000);
  });

  test('no critical accessibility violations', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // Basic accessibility checks
    
    // Should have proper document structure
    const title = await page.title();
    expect(title).toBeTruthy();
    expect(title.length).toBeGreaterThan(0);
    
    // Should have proper heading hierarchy
    const h1Count = await page.locator('h1').count();
    expect(h1Count).toBe(1);
    
    // Images should have alt text (if any)
    const images = await page.locator('img').all();
    for (const img of images) {
      if (await img.isVisible()) {
        const altText = await img.getAttribute('alt');
        expect(altText).not.toBeNull(); // Should have alt attribute (can be empty for decorative)
      }
    }
    
    // Buttons should have accessible names
    const buttons = await page.locator('button').all();
    for (const button of buttons) {
      if (await button.isVisible()) {
        const accessibleName = await button.evaluate(el => {
          return el.getAttribute('aria-label') || 
                 el.textContent?.trim() || 
                 el.getAttribute('title');
        });
        expect(accessibleName).toBeTruthy();
      }
    }
  });

  test('no JavaScript runtime errors', async ({ page }) => {
    const jsErrors: string[] = [];
    const unhandledRejections: string[] = [];
    
    page.on('console', msg => {
      if (msg.type() === 'error') {
        jsErrors.push(msg.text());
      }
    });
    
    page.on('pageerror', error => {
      jsErrors.push(error.message);
    });
    
    page.on('requestfailed', request => {
      // Only log failed requests that aren't expected (like API calls we're mocking)
      if (!request.url().includes('/api/')) {
        jsErrors.push(`Failed request: ${request.url()}`);
      }
    });
    
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(3000);
    
    // Interact with the application to trigger potential errors
    const refreshButton = page.getByRole('button', { name: /refresh/i });
    if (await refreshButton.isVisible()) {
      await refreshButton.click();
      await page.waitForTimeout(1000);
    }
    
    const taskElement = page.getByText('Smoke Test Task').first();
    if (await taskElement.isVisible()) {
      await taskElement.click();
      await page.waitForTimeout(500);
      
      const modal = page.getByRole('dialog');
      if (await modal.isVisible()) {
        await page.keyboard.press('Escape');
      }
    }
    
    // Filter out expected/harmless errors
    const criticalErrors = jsErrors.filter(error => 
      !error.includes('favicon') && 
      !error.includes('chrome-extension') &&
      !error.includes('Non-Error promise rejection') &&
      !error.includes('ResizeObserver loop limit exceeded') &&
      !error.toLowerCase().includes('network error')
    );
    
    expect(criticalErrors).toHaveLength(0);
  });

  test('critical user journeys work end-to-end', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // Journey 1: View task details
    const task = page.getByText('Smoke Test Task').first();
    if (await task.isVisible()) {
      await task.click();
      
      const modal = page.getByRole('dialog');
      if (await modal.isVisible()) {
        // Should show task information
        await expect(modal).toContainText('Smoke Test Task');
        await expect(modal).toContainText('Critical path validation task');
        
        // Close modal
        await page.keyboard.press('Escape');
        await expect(modal).not.toBeVisible();
      }
    }
    
    // Journey 2: Refresh data
    const refreshButton = page.getByRole('button', { name: /refresh/i });
    if (await refreshButton.isVisible()) {
      await refreshButton.click();
      await expect(refreshButton).toBeDisabled();
      
      await page.waitForTimeout(1500);
      await expect(refreshButton).toBeEnabled();
      
      // Data should still be visible after refresh
      await expect(page.getByText('Smoke Test Task')).toBeVisible();
    }
    
    // Journey 3: Open and close settings
    const settingsButton = page.getByRole('button', { name: /settings/i });
    if (await settingsButton.isVisible()) {
      await settingsButton.click();
      
      const settingsModal = page.getByRole('dialog');
      if (await settingsModal.isVisible()) {
        // Settings modal should be functional
        await expect(settingsModal).toContainText(/setting/i);
        
        // Close settings
        await page.keyboard.press('Escape');
        await expect(settingsModal).not.toBeVisible();
      }
    }
    
    // All journeys completed successfully
    expect(await page.locator('body').isVisible()).toBe(true);
  });
});