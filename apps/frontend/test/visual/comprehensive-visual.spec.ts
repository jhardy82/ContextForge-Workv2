import { test, expect } from '@playwright/test';

/**
 * Comprehensive Visual Regression Testing Suite
 * Tests visual consistency across components, states, themes,
 * viewports, and user interactions
 */
test.describe('Comprehensive Visual Regression Tests', () => {
  
  test.beforeEach(async ({ page }) => {
    // Setup consistent mock API responses for visual consistency
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
            name: 'Visual Test Project Alpha',
            description: 'Testing visual consistency with structured data',
            status: 'active',
            created: '2024-01-15T10:00:00Z',
            updated: '2024-01-15T15:30:00Z'
          },
          {
            id: '2',
            name: 'Visual Test Project Beta',
            description: 'Secondary project for visual regression testing',
            status: 'inactive',
            created: '2024-01-10T08:00:00Z',
            updated: '2024-01-14T12:00:00Z'
          }
        ]
      });
    });

    await page.route('**/api/v1/tasks', async route => {
      await route.fulfill({
        json: [
          {
            id: '1',
            title: 'Critical Visual Component Task',
            description: 'Ensure all visual components render consistently across browsers and viewports',
            status: 'new',
            priority: 'high',
            projectId: '1',
            created: '2024-01-15T09:00:00Z',
            updated: '2024-01-15T14:00:00Z',
            assignee: 'visual-tester-alpha',
            tags: ['ui', 'visual', 'critical']
          },
          {
            id: '2',
            title: 'Layout Stability Verification',
            description: 'Verify that layout remains stable during interactions and state changes',
            status: 'in-progress',
            priority: 'medium',
            projectId: '1',
            created: '2024-01-15T10:30:00Z',
            updated: '2024-01-15T16:15:00Z',
            assignee: 'layout-specialist',
            tags: ['layout', 'stability', 'responsive']
          },
          {
            id: '3',
            title: 'Theme Consistency Check',
            description: 'Validate theme colors and typography across all components',
            status: 'completed',
            priority: 'low',
            projectId: '2',
            created: '2024-01-12T14:00:00Z',
            updated: '2024-01-14T11:30:00Z',
            assignee: 'theme-designer',
            tags: ['theme', 'colors', 'typography']
          },
          {
            id: '4',
            title: 'Interactive Element States',
            description: 'Test hover, focus, and active states for all interactive elements',
            status: 'blocked',
            priority: 'high',
            projectId: '1',
            created: '2024-01-14T16:00:00Z',
            updated: '2024-01-15T13:45:00Z',
            assignee: 'interaction-designer',
            tags: ['interaction', 'states', 'accessibility']
          }
        ]
      });
    });

    // Set development mode consistently
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

  test('main dashboard layout - desktop', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000); // Allow for animations and loading states
    
    // Hide dynamic elements that might cause flakiness
    await page.addStyleTag({
      content: `
        [data-testid="timestamp"],
        .timestamp,
        .relative-time,
        [data-dynamic="true"] {
          visibility: hidden !important;
        }
      `
    });
    
    // Take full page screenshot
    await expect(page).toHaveScreenshot('dashboard-desktop-full.png', {
      fullPage: true,
      animations: 'disabled'
    });
    
    // Take screenshot of main content area only
    const mainContent = page.locator('main, [role="main"], .main-content').first();
    if (await mainContent.isVisible()) {
      await expect(mainContent).toHaveScreenshot('dashboard-desktop-main.png', {
        animations: 'disabled'
      });
    }
  });

  test('main dashboard layout - tablet', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    await page.addStyleTag({
      content: `
        [data-testid="timestamp"],
        .timestamp,
        .relative-time,
        [data-dynamic="true"] {
          visibility: hidden !important;
        }
      `
    });
    
    await expect(page).toHaveScreenshot('dashboard-tablet-full.png', {
      fullPage: true,
      animations: 'disabled'
    });
  });

  test('main dashboard layout - mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    await page.addStyleTag({
      content: `
        [data-testid="timestamp"],
        .timestamp,
        .relative-time,
        [data-dynamic="true"] {
          visibility: hidden !important;
        }
      `
    });
    
    await expect(page).toHaveScreenshot('dashboard-mobile-full.png', {
      fullPage: true,
      animations: 'disabled'
    });
  });

  test('task list component states', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // Hide dynamic timestamps
    await page.addStyleTag({
      content: `
        [data-testid="timestamp"],
        .timestamp,
        .relative-time {
          visibility: hidden !important;
        }
      `
    });
    
    // Screenshot of task list in default state
    const taskList = page.locator('[data-testid="task-list"], .task-list, .tasks').first();
    if (await taskList.isVisible()) {
      await expect(taskList).toHaveScreenshot('task-list-default.png', {
        animations: 'disabled'
      });
    }
    
    // Test task list with search/filter applied
    const searchInput = page.locator('input[placeholder*="search"], input[placeholder*="filter"]').first();
    if (await searchInput.isVisible()) {
      await searchInput.fill('Visual');
      await page.waitForTimeout(500);
      
      if (await taskList.isVisible()) {
        await expect(taskList).toHaveScreenshot('task-list-filtered.png', {
          animations: 'disabled'
        });
      }
      
      // Clear search
      await searchInput.clear();
      await page.waitForTimeout(500);
    }
  });

  test('task modal component states', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // Hide dynamic timestamps
    await page.addStyleTag({
      content: `
        [data-testid="timestamp"],
        .timestamp,
        .relative-time {
          visibility: hidden !important;
        }
      `
    });
    
    // Click on first task to open modal
    const firstTask = page.getByText('Critical Visual Component Task').first();
    if (await firstTask.isVisible()) {
      await firstTask.click();
      await page.waitForTimeout(500);
      
      // Screenshot of modal
      const modal = page.getByRole('dialog');
      if (await modal.isVisible()) {
        await expect(modal).toHaveScreenshot('task-modal-detailed.png', {
          animations: 'disabled'
        });
        
        // Close modal
        await page.keyboard.press('Escape');
        await page.waitForTimeout(500);
      }
    }
    
    // Test different task states
    const taskStates = [
      { text: 'Layout Stability Verification', status: 'in-progress' },
      { text: 'Theme Consistency Check', status: 'completed' },
      { text: 'Interactive Element States', status: 'blocked' }
    ];
    
    for (const taskState of taskStates) {
      const task = page.getByText(taskState.text).first();
      if (await task.isVisible()) {
        await task.click();
        await page.waitForTimeout(500);
        
        const modal = page.getByRole('dialog');
        if (await modal.isVisible()) {
          await expect(modal).toHaveScreenshot(`task-modal-${taskState.status}.png`, {
            animations: 'disabled'
          });
          
          await page.keyboard.press('Escape');
          await page.waitForTimeout(500);
        }
      }
    }
  });

  test('connection status component states', async ({ page }) => {
    // Test connected state
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    const connectionStatus = page.locator('[data-testid="connection-status"], .connection-status, .status-indicator').first();
    if (await connectionStatus.isVisible()) {
      await expect(connectionStatus).toHaveScreenshot('connection-status-connected.png', {
        animations: 'disabled'
      });
    }
    
    // Test disconnected state
    await page.route('**/api/v1/health', async route => {
      await route.fulfill({
        status: 500,
        json: { error: 'Connection failed' }
      });
    });
    
    // Trigger refresh to show disconnected state
    const refreshButton = page.getByRole('button', { name: /refresh/i });
    if (await refreshButton.isVisible()) {
      await refreshButton.click();
      await page.waitForTimeout(2000);
      
      if (await connectionStatus.isVisible()) {
        await expect(connectionStatus).toHaveScreenshot('connection-status-disconnected.png', {
          animations: 'disabled'
        });
      }
    }
  });

  test('settings modal component', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
    
    // Open settings modal
    const settingsButton = page.getByRole('button', { name: /settings/i });
    if (await settingsButton.isVisible()) {
      await settingsButton.click();
      await page.waitForTimeout(500);
      
      const settingsModal = page.getByRole('dialog');
      if (await settingsModal.isVisible()) {
        await expect(settingsModal).toHaveScreenshot('settings-modal.png', {
          animations: 'disabled'
        });
        
        // Test with different settings
        const autoRefreshToggle = page.getByLabel(/auto.?refresh/i);
        if (await autoRefreshToggle.isVisible()) {
          if (await autoRefreshToggle.isChecked()) {
            await autoRefreshToggle.uncheck();
          } else {
            await autoRefreshToggle.check();
          }
          await page.waitForTimeout(300);
          
          await expect(settingsModal).toHaveScreenshot('settings-modal-modified.png', {
            animations: 'disabled'
          });
        }
        
        await page.keyboard.press('Escape');
      }
    }
  });

  test('button and interactive states', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // Hide dynamic content
    await page.addStyleTag({
      content: `
        [data-testid="timestamp"],
        .timestamp,
        .relative-time {
          visibility: hidden !important;
        }
      `
    });
    
    // Test refresh button states
    const refreshButton = page.getByRole('button', { name: /refresh/i });
    if (await refreshButton.isVisible()) {
      // Default state
      await expect(refreshButton).toHaveScreenshot('button-refresh-default.png', {
        animations: 'disabled'
      });
      
      // Hover state
      await refreshButton.hover();
      await page.waitForTimeout(300);
      await expect(refreshButton).toHaveScreenshot('button-refresh-hover.png', {
        animations: 'disabled'
      });
      
      // Focus state
      await refreshButton.focus();
      await page.waitForTimeout(300);
      await expect(refreshButton).toHaveScreenshot('button-refresh-focus.png', {
        animations: 'disabled'
      });
      
      // Click and test loading/disabled state
      await refreshButton.click();
      await page.waitForTimeout(200); // Catch loading state
      
      if (await refreshButton.isDisabled()) {
        await expect(refreshButton).toHaveScreenshot('button-refresh-disabled.png', {
          animations: 'disabled'
        });
      }
    }
    
    // Test settings button
    const settingsButton = page.getByRole('button', { name: /settings/i });
    if (await settingsButton.isVisible()) {
      await expect(settingsButton).toHaveScreenshot('button-settings-default.png', {
        animations: 'disabled'
      });
      
      await settingsButton.hover();
      await page.waitForTimeout(300);
      await expect(settingsButton).toHaveScreenshot('button-settings-hover.png', {
        animations: 'disabled'
      });
    }
  });

  test('loading and empty states', async ({ page }) => {
    // Test loading state by delaying API responses
    await page.route('**/api/v1/tasks', async route => {
      await page.waitForTimeout(2000); // Simulate slow network
      await route.fulfill({
        json: []
      });
    });
    
    await page.goto('/');
    await page.waitForTimeout(1000); // Catch loading state
    
    // Try to capture loading state
    const loadingIndicator = page.locator('.loading, [data-testid="loading"], .spinner, .skeleton').first();
    if (await loadingIndicator.isVisible()) {
      await expect(loadingIndicator).toHaveScreenshot('loading-state.png', {
        animations: 'disabled'
      });
    }
    
    // Wait for loading to complete and show empty state
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // Screenshot of empty state
    const emptyState = page.locator('.empty-state, [data-testid="empty"], .no-tasks').first();
    if (await emptyState.isVisible()) {
      await expect(emptyState).toHaveScreenshot('empty-state-tasks.png', {
        animations: 'disabled'
      });
    } else {
      // If no specific empty state component, screenshot the main content
      const mainContent = page.locator('main, [role="main"], .main-content').first();
      if (await mainContent.isVisible()) {
        await expect(mainContent).toHaveScreenshot('empty-state-general.png', {
          animations: 'disabled'
        });
      }
    }
  });

  test('task status badges and indicators', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // Hide dynamic timestamps
    await page.addStyleTag({
      content: `
        [data-testid="timestamp"],
        .timestamp,
        .relative-time {
          visibility: hidden !important;
        }
      `
    });
    
    // Find and screenshot different status badges
    const statusTypes = ['new', 'in-progress', 'completed', 'blocked'];
    
    for (const status of statusTypes) {
      const statusBadge = page.locator(`[data-status="${status}"], .status-${status}, .badge-${status}`).first();
      if (await statusBadge.isVisible()) {
        await expect(statusBadge).toHaveScreenshot(`status-badge-${status}.png`, {
          animations: 'disabled'
        });
      } else {
        // Try to find status by text content
        const statusByText = page.locator('.badge, .status, .chip').filter({ hasText: status }).first();
        if (await statusByText.isVisible()) {
          await expect(statusByText).toHaveScreenshot(`status-badge-${status}.png`, {
            animations: 'disabled'
          });
        }
      }
    }
    
    // Priority indicators
    const priorityTypes = ['high', 'medium', 'low'];
    
    for (const priority of priorityTypes) {
      const priorityBadge = page.locator(`[data-priority="${priority}"], .priority-${priority}, [title*="${priority}"]`).first();
      if (await priorityBadge.isVisible()) {
        await expect(priorityBadge).toHaveScreenshot(`priority-badge-${priority}.png`, {
          animations: 'disabled'
        });
      }
    }
  });

  test('responsive layout breakpoints', async ({ page }) => {
    const breakpoints = [
      { name: 'mobile-sm', width: 320, height: 568 },
      { name: 'mobile-lg', width: 414, height: 896 },
      { name: 'tablet-sm', width: 768, height: 1024 },
      { name: 'tablet-lg', width: 1024, height: 768 },
      { name: 'desktop-sm', width: 1280, height: 720 },
      { name: 'desktop-lg', width: 1920, height: 1080 }
    ];
    
    for (const breakpoint of breakpoints) {
      await page.setViewportSize({ width: breakpoint.width, height: breakpoint.height });
      await page.goto('/');
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(1000);
      
      // Hide dynamic content
      await page.addStyleTag({
        content: `
          [data-testid="timestamp"],
          .timestamp,
          .relative-time {
            visibility: hidden !important;
          }
        `
      });
      
      await expect(page).toHaveScreenshot(`layout-${breakpoint.name}.png`, {
        fullPage: true,
        animations: 'disabled'
      });
    }
  });

  test('extension server layout - production mode', async ({ page }) => {
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
    
    // Should show extension server, not DTM dashboard
    await expect(page).toHaveScreenshot('extension-server-main.png', {
      fullPage: true,
      animations: 'disabled'
    });
    
    // Test extension selection
    const extensionItem = page.getByText('VS Code TODOs').first();
    if (await extensionItem.isVisible()) {
      await extensionItem.click();
      await page.waitForTimeout(500);
      
      await expect(page).toHaveScreenshot('extension-server-selected.png', {
        fullPage: true,
        animations: 'disabled'
      });
    }
  });

  test('focus indicators and accessibility visuals', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // Test focus indicators on interactive elements
    const interactiveElements = await page.locator('button, a, input, select, [tabindex="0"]').all();
    
    for (let i = 0; i < Math.min(interactiveElements.length, 5); i++) {
      const element = interactiveElements[i];
      if (await element.isVisible()) {
        await element.focus();
        await page.waitForTimeout(300);
        
        const tagName = await element.evaluate(el => el.tagName.toLowerCase());
        const role = await element.getAttribute('role') || tagName;
        
        await expect(element).toHaveScreenshot(`focus-${role}-${i}.png`, {
          animations: 'disabled'
        });
      }
    }
  });

  test('dark mode compatibility', async ({ page }) => {
    // Simulate dark mode preference
    await page.emulateMedia({ colorScheme: 'dark' });
    
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // Hide dynamic content
    await page.addStyleTag({
      content: `
        [data-testid="timestamp"],
        .timestamp,
        .relative-time {
          visibility: hidden !important;
        }
      `
    });
    
    await expect(page).toHaveScreenshot('dashboard-dark-mode.png', {
      fullPage: true,
      animations: 'disabled'
    });
    
    // Test modal in dark mode
    const firstTask = page.getByText('Critical Visual Component Task').first();
    if (await firstTask.isVisible()) {
      await firstTask.click();
      await page.waitForTimeout(500);
      
      const modal = page.getByRole('dialog');
      if (await modal.isVisible()) {
        await expect(modal).toHaveScreenshot('task-modal-dark-mode.png', {
          animations: 'disabled'
        });
        
        await page.keyboard.press('Escape');
      }
    }
  });

  test('high contrast mode compatibility', async ({ page }) => {
    // Simulate high contrast preference
    await page.emulateMedia({ colorScheme: 'light', forcedColors: 'active' });
    
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // Hide dynamic content
    await page.addStyleTag({
      content: `
        [data-testid="timestamp"],
        .timestamp,
        .relative-time {
          visibility: hidden !important;
        }
      `
    });
    
    await expect(page).toHaveScreenshot('dashboard-high-contrast.png', {
      fullPage: true,
      animations: 'disabled'
    });
  });
});