import { test, expect } from '@playwright/test';

/**
 * DTM Visual Regression Tests
 * Tests visual consistency across different states and screen sizes
 */
test.describe('DTM Visual Regression', () => {
  test.beforeEach(async ({ page }) => {
    // Mock API responses for consistent visual tests
    await page.route('**/api/v1/health', async route => {
      await route.fulfill({
        json: { version: '1.0.0', uptime: '24 hours' }
      });
    });

    await page.route('**/api/v1/projects', async route => {
      await route.fulfill({
        json: [
          {
            id: 'P-VISUAL-001',
            name: 'Visual Test Project',
            description: 'Project for visual regression testing',
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
            id: 'T-VISUAL-001',
            title: 'Visual Test Task',
            description: 'Task for visual regression testing',
            status: 'new',
            priority: 'high',
            shape: 'Triangle',
            project_id: 'P-VISUAL-001',
            created_at: '2024-01-01T00:00:00Z'
          },
          {
            id: 'T-VISUAL-002',
            title: 'Another Visual Task',
            description: 'Second task for testing',
            status: 'in_progress',
            priority: 'medium',
            shape: 'Circle',
            project_id: 'P-VISUAL-001',
            created_at: '2024-01-01T00:00:00Z'
          }
        ]
      });
    });

    // Set development mode
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

    await page.goto('/');
  });

  test('DTM dashboard initial state', async ({ page }) => {
    // Wait for content to load
    await page.waitForTimeout(2000);
    
    // Take screenshot of initial dashboard state
    await expect(page).toHaveScreenshot('dtm-dashboard-initial.png');
  });

  test('DTM dashboard with connection status', async ({ page }) => {
    // Wait for connection check
    await page.waitForTimeout(2000);
    
    // Take screenshot showing connection status
    await expect(page.locator('[data-testid="connection-status"]')).toHaveScreenshot('connection-status.png');
  });

  test('Task tree with different statuses', async ({ page }) => {
    // Wait for tasks to load
    await page.waitForTimeout(2000);
    
    // Take screenshot of task tree
    await expect(page.locator('[data-testid="task-tree"]')).toHaveScreenshot('task-tree.png');
  });

  test('Task detail modal', async ({ page }) => {
    // Wait for tasks to load
    await page.waitForTimeout(2000);
    
    // Open task detail modal
    await page.getByText('Visual Test Task').click();
    
    // Wait for modal to open
    await page.waitForSelector('[role="dialog"]');
    
    // Take screenshot of modal
    await expect(page.locator('[role="dialog"]')).toHaveScreenshot('task-detail-modal.png');
  });

  test('Settings modal', async ({ page }) => {
    // Wait for initial load
    await page.waitForTimeout(1000);
    
    // Open settings modal
    await page.getByRole('button', { name: /settings/i }).click();
    
    // Wait for modal to open
    await page.waitForSelector('[role="dialog"]');
    
    // Take screenshot of settings modal
    await expect(page.locator('[role="dialog"]')).toHaveScreenshot('settings-modal.png');
  });

  test('Mobile viewport - dashboard', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await page.waitForTimeout(1000);
    
    // Take screenshot of mobile dashboard
    await expect(page).toHaveScreenshot('dtm-dashboard-mobile.png');
  });

  test('Tablet viewport - dashboard', async ({ page }) => {
    // Set tablet viewport
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.waitForTimeout(1000);
    
    // Take screenshot of tablet dashboard
    await expect(page).toHaveScreenshot('dtm-dashboard-tablet.png');
  });

  test('Desktop wide viewport - dashboard', async ({ page }) => {
    // Set wide desktop viewport
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.waitForTimeout(1000);
    
    // Take screenshot of wide desktop dashboard
    await expect(page).toHaveScreenshot('dtm-dashboard-wide.png');
  });

  test('Dark theme support', async ({ page }) => {
    // Add dark theme class if supported
    await page.addInitScript(() => {
      document.documentElement.classList.add('dark');
    });
    
    await page.waitForTimeout(1000);
    
    // Take screenshot with dark theme
    await expect(page).toHaveScreenshot('dtm-dashboard-dark.png');
  });

  test('High contrast mode', async ({ page }) => {
    // Simulate high contrast preference
    await page.emulateMedia({ reducedMotion: 'reduce', colorScheme: 'dark' });
    
    await page.waitForTimeout(1000);
    
    // Take screenshot in high contrast mode
    await expect(page).toHaveScreenshot('dtm-dashboard-high-contrast.png');
  });

  test('Loading states', async ({ page }) => {
    // Mock slow API responses
    await page.route('**/api/v1/**', async route => {
      await new Promise(resolve => setTimeout(resolve, 2000));
      await route.fulfill({ json: [] });
    });
    
    await page.reload();
    
    // Take screenshot of loading state
    await expect(page).toHaveScreenshot('dtm-dashboard-loading.png');
  });

  test('Error states', async ({ page }) => {
    // Mock API errors
    await page.route('**/api/v1/health', async route => {
      await route.fulfill({
        status: 500,
        json: { error: 'Server error' }
      });
    });
    
    await page.reload();
    await page.waitForTimeout(2000);
    
    // Take screenshot of error state
    await expect(page).toHaveScreenshot('dtm-dashboard-error.png');
  });

  test('Empty states', async ({ page }) => {
    // Mock empty responses
    await page.route('**/api/v1/projects', async route => {
      await route.fulfill({ json: [] });
    });
    
    await page.route('**/api/v1/tasks', async route => {
      await route.fulfill({ json: [] });
    });
    
    await page.reload();
    await page.waitForTimeout(2000);
    
    // Take screenshot of empty state
    await expect(page).toHaveScreenshot('dtm-dashboard-empty.png');
  });

  test('Focus states for accessibility', async ({ page }) => {
    await page.waitForTimeout(1000);
    
    // Focus on refresh button
    await page.getByRole('button', { name: /refresh/i }).focus();
    
    // Take screenshot showing focus state
    await expect(page).toHaveScreenshot('dtm-dashboard-focus.png');
  });

  test('Hover states', async ({ page }) => {
    await page.waitForTimeout(2000);
    
    // Hover over a task
    await page.getByText('Visual Test Task').hover();
    
    // Take screenshot showing hover state
    await expect(page).toHaveScreenshot('task-hover-state.png');
  });

  test('Production mode - extension server', async ({ page }) => {
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
    await page.waitForTimeout(1000);
    
    // Take screenshot of extension server
    await expect(page).toHaveScreenshot('extension-server-production.png');
  });
});