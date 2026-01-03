import { Page, expect } from '@playwright/test';

/**
 * Common test utilities and helpers for Playwright tests
 */

export class TestHelpers {
  constructor(private page: Page) {}

  /**
   * Set up common mock API responses for DTM testing
   */
  async setupDTMMocks(options: {
    projectCount?: number;
    taskCount?: number;
    includeErrors?: boolean;
    responseDelay?: number;
  } = {}): Promise<void> {
    const {
      projectCount = 3,
      taskCount = 10,
      includeErrors = false,
      responseDelay = 0
    } = options;

    // Health check mock
    await this.page.route('**/api/v1/health', async route => {
      if (responseDelay > 0) {
        await new Promise(resolve => setTimeout(resolve, responseDelay));
      }
      
      if (includeErrors) {
        await route.fulfill({
          status: 500,
          json: { error: 'Server error' }
        });
      } else {
        await route.fulfill({
          json: { version: '1.0.0', uptime: '24 hours' }
        });
      }
    });

    // Projects mock
    await this.page.route('**/api/v1/projects', async route => {
      if (responseDelay > 0) {
        await new Promise(resolve => setTimeout(resolve, responseDelay));
      }

      const projects = Array.from({ length: projectCount }, (_, i) => ({
        id: `P-TEST-${i.toString().padStart(3, '0')}`,
        name: `Test Project ${i + 1}`,
        description: `Description for test project ${i + 1}`,
        status: ['active', 'completed', 'inactive'][i % 3],
        created_at: new Date(Date.now() - i * 86400000).toISOString()
      }));

      await route.fulfill({ json: projects });
    });

    // Tasks mock
    await this.page.route('**/api/v1/tasks', async route => {
      if (responseDelay > 0) {
        await new Promise(resolve => setTimeout(resolve, responseDelay));
      }

      const tasks = Array.from({ length: taskCount }, (_, i) => ({
        id: `T-TEST-${i.toString().padStart(3, '0')}`,
        title: `Test Task ${i + 1}`,
        description: `Description for test task ${i + 1}`,
        status: ['new', 'in_progress', 'pending', 'completed', 'blocked'][i % 5],
        priority: ['low', 'medium', 'high', 'critical'][i % 4],
        shape: ['Triangle', 'Circle', 'Spiral', 'Pentagon', 'Fractal'][i % 5],
        project_id: `P-TEST-${Math.floor(i / 4).toString().padStart(3, '0')}`,
        created_at: new Date(Date.now() - i * 3600000).toISOString(),
        updated_at: new Date(Date.now() - i * 1800000).toISOString()
      }));

      await route.fulfill({ json: tasks });
    });
  }

  /**
   * Set development mode for testing DTM dashboard
   */
  async setDevelopmentMode(): Promise<void> {
    await this.page.addInitScript(() => {
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
  }

  /**
   * Set production mode for testing extension server
   */
  async setProductionMode(): Promise<void> {
    await this.page.addInitScript(() => {
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
  }

  /**
   * Wait for DTM dashboard to load completely
   */
  async waitForDTMDashboard(): Promise<void> {
    await expect(this.page.getByRole('heading', { name: /dtm task manager/i })).toBeVisible();
    await this.page.waitForTimeout(2000); // Allow time for API calls
  }

  /**
   * Wait for extension server to load completely
   */
  async waitForExtensionServer(): Promise<void> {
    await expect(this.page.getByRole('heading', { name: /vs code extension server/i })).toBeVisible();
    await expect(this.page.getByText('Available Extensions')).toBeVisible();
  }

  /**
   * Open and verify task detail modal
   */
  async openTaskModal(taskTitle: string): Promise<void> {
    await this.page.getByText(taskTitle).click();
    await expect(this.page.getByRole('dialog')).toBeVisible();
    await expect(this.page.getByText(taskTitle)).toBeVisible();
  }

  /**
   * Close modal using various methods
   */
  async closeModal(method: 'escape' | 'click' | 'button' = 'escape'): Promise<void> {
    switch (method) {
      case 'escape':
        await this.page.keyboard.press('Escape');
        break;
      case 'click':
        await this.page.locator('[role="dialog"] ~ div').click(); // Click backdrop
        break;
      case 'button':
        const closeButton = this.page.getByRole('button', { name: /close|×/i }).first();
        await closeButton.click();
        break;
    }
    
    await expect(this.page.getByRole('dialog')).not.toBeVisible();
  }

  /**
   * Verify no console errors (with optional filtering)
   */
  async checkConsoleErrors(ignorePatterns: string[] = []): Promise<string[]> {
    const errors: string[] = [];
    
    this.page.on('console', msg => {
      if (msg.type() === 'error') {
        const text = msg.text();
        const shouldIgnore = ignorePatterns.some(pattern => text.includes(pattern));
        if (!shouldIgnore) {
          errors.push(text);
        }
      }
    });

    this.page.on('pageerror', error => {
      const shouldIgnore = ignorePatterns.some(pattern => error.message.includes(pattern));
      if (!shouldIgnore) {
        errors.push(error.message);
      }
    });

    return errors;
  }

  /**
   * Simulate network conditions
   */
  async simulateNetworkConditions(condition: 'offline' | 'slow' | 'fast'): Promise<void> {
    switch (condition) {
      case 'offline':
        await this.page.context().setOffline(true);
        break;
      case 'slow':
        await this.page.route('**/*', async route => {
          await new Promise(resolve => setTimeout(resolve, 2000));
          await route.continue();
        });
        break;
      case 'fast':
        await this.page.context().setOffline(false);
        await this.page.unroute('**/*');
        break;
    }
  }

  /**
   * Take a screenshot with consistent naming
   */
  async takeScreenshot(name: string, fullPage = false): Promise<void> {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `${name}-${timestamp}.png`;
    
    await this.page.screenshot({
      path: `test-results/screenshots/${filename}`,
      fullPage
    });
  }

  /**
   * Measure performance metrics
   */
  async measurePerformance(): Promise<{
    loadTime: number;
    domContentLoaded: number;
    firstContentfulPaint?: number;
    networkRequests: number;
  }> {
    const performanceTiming = await this.page.evaluate(() => {
      const nav = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
      return {
        loadTime: nav.loadEventEnd - nav.fetchStart,
        domContentLoaded: nav.domContentLoadedEventEnd - nav.fetchStart
      };
    });

    const paintTiming = await this.page.evaluate(() => {
      const paintEntries = performance.getEntriesByType('paint');
      const fcp = paintEntries.find(entry => entry.name === 'first-contentful-paint');
      return fcp ? fcp.startTime : undefined;
    });

    const networkRequests = await this.page.evaluate(() => {
      return performance.getEntriesByType('resource').length;
    });

    return {
      ...performanceTiming,
      firstContentfulPaint: paintTiming,
      networkRequests
    };
  }

  /**
   * Test keyboard navigation
   */
  async testKeyboardNavigation(): Promise<void> {
    // Test tab navigation
    await this.page.keyboard.press('Tab');
    let focusedElement = this.page.locator(':focus');
    await expect(focusedElement).toBeVisible();

    // Test arrow keys if applicable
    await this.page.keyboard.press('ArrowDown');
    
    // Test Enter activation
    await this.page.keyboard.press('Enter');
    
    // Test Escape to close any opened elements
    await this.page.keyboard.press('Escape');
  }

  /**
   * Verify responsive design at different breakpoints
   */
  async testResponsiveDesign(): Promise<void> {
    const breakpoints = [
      { name: 'mobile', width: 375, height: 667 },
      { name: 'tablet', width: 768, height: 1024 },
      { name: 'desktop', width: 1200, height: 800 },
      { name: 'wide', width: 1920, height: 1080 }
    ];

    for (const breakpoint of breakpoints) {
      await this.page.setViewportSize({ width: breakpoint.width, height: breakpoint.height });
      await this.page.waitForTimeout(500);
      
      // Verify content is still accessible
      const heading = this.page.getByRole('heading').first();
      await expect(heading).toBeVisible();
      
      await this.takeScreenshot(`responsive-${breakpoint.name}`);
    }
  }

  /**
   * Test accessibility features
   */
  async testAccessibility(): Promise<void> {
    // Check for skip links
    const skipLinks = this.page.locator('a[href^="#"]').filter({ hasText: /skip/i });
    if (await skipLinks.count() > 0) {
      await skipLinks.first().focus();
      await expect(skipLinks.first()).toBeFocused();
    }

    // Test heading hierarchy
    const headings = await this.page.locator('h1, h2, h3, h4, h5, h6').all();
    const headingLevels = await Promise.all(
      headings.map(async (heading) => {
        const tagName = await heading.evaluate(el => el.tagName.toLowerCase());
        return parseInt(tagName.charAt(1));
      })
    );

    // Verify heading hierarchy is logical
    for (let i = 1; i < headingLevels.length; i++) {
      const current = headingLevels[i];
      const previous = headingLevels[i - 1];
      expect(current - previous).toBeLessThanOrEqual(1);
    }
  }

  /**
   * Mock authentication state
   */
  async setAuthenticationState(isAuthenticated = true, userInfo?: any): Promise<void> {
    await this.page.addInitScript((auth) => {
      if (auth.isAuthenticated && window.spark) {
        window.spark.user = async () => ({
          login: auth.userInfo?.login || 'testuser',
          email: auth.userInfo?.email || 'test@example.com',
          avatarUrl: auth.userInfo?.avatarUrl || 'https://github.com/ghost.png',
          id: auth.userInfo?.id || '12345',
          isOwner: auth.userInfo?.isOwner || true
        });
      }
    }, { isAuthenticated, userInfo });
  }

  /**
   * Wait for API requests to complete
   */
  async waitForAPIRequests(timeout = 5000): Promise<void> {
    await this.page.waitForLoadState('networkidle', { timeout });
  }

  /**
   * Simulate user interactions with realistic delays
   */
  async simulateUserInteraction(action: 'click' | 'type' | 'scroll', target: string, value?: string): Promise<void> {
    // Add realistic human delays
    await this.page.waitForTimeout(100 + Math.random() * 200);
    
    switch (action) {
      case 'click':
        await this.page.locator(target).click();
        break;
      case 'type':
        if (value) {
          await this.page.locator(target).fill('');
          await this.page.locator(target).type(value, { delay: 50 });
        }
        break;
      case 'scroll':
        await this.page.locator(target).scrollIntoViewIfNeeded();
        break;
    }
    
    await this.page.waitForTimeout(50 + Math.random() * 100);
  }
}

/**
 * Data generation utilities
 */
export class TestDataGenerator {
  static generateProject(id: string, overrides: Partial<any> = {}) {
    return {
      id,
      name: `Test Project ${id}`,
      description: `Generated test project with ID ${id}`,
      status: 'active',
      created_at: new Date().toISOString(),
      ...overrides
    };
  }

  static generateTask(id: string, projectId: string, overrides: Partial<any> = {}) {
    return {
      id,
      title: `Test Task ${id}`,
      description: `Generated test task with ID ${id}`,
      status: 'new',
      priority: 'medium',
      shape: 'Circle',
      project_id: projectId,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      ...overrides
    };
  }

  static generateLargeDataset(projectCount = 10, tasksPerProject = 20) {
    const projects = Array.from({ length: projectCount }, (_, i) =>
      this.generateProject(`P-LARGE-${i.toString().padStart(3, '0')}`)
    );

    const tasks = projects.flatMap((project, i) =>
      Array.from({ length: tasksPerProject }, (_, j) =>
        this.generateTask(
          `T-LARGE-${(i * tasksPerProject + j).toString().padStart(3, '0')}`,
          project.id,
          {
            status: ['new', 'in_progress', 'pending', 'completed', 'blocked'][j % 5],
            priority: ['low', 'medium', 'high', 'critical'][j % 4]
          }
        )
      )
    );

    return { projects, tasks };
  }
}

/**
 * Assertion helpers
 */
export class TestAssertions {
  constructor(private page: Page) {}

  async assertNoAccessibilityViolations(): Promise<void> {
    // This would integrate with axe-core if available
    // For now, check basic accessibility requirements
    
    // Check for h1
    const h1Count = await this.page.locator('h1').count();
    expect(h1Count).toBeGreaterThan(0);

    // Check interactive elements have proper labels
    const buttons = await this.page.getByRole('button').all();
    for (const button of buttons) {
      const accessibleName = await button.getAttribute('aria-label') || 
                            await button.textContent() ||
                            await button.getAttribute('title');
      expect(accessibleName).toBeTruthy();
    }
  }

  async assertPerformanceThresholds(metrics: {
    loadTime?: number;
    fcp?: number;
    networkRequests?: number;
  }): Promise<void> {
    const performance = await new TestHelpers(this.page).measurePerformance();
    
    if (metrics.loadTime) {
      expect(performance.loadTime).toBeLessThan(metrics.loadTime);
    }
    
    if (metrics.fcp && performance.firstContentfulPaint) {
      expect(performance.firstContentfulPaint).toBeLessThan(metrics.fcp);
    }
    
    if (metrics.networkRequests) {
      expect(performance.networkRequests).toBeLessThan(metrics.networkRequests);
    }
  }

  async assertNoConsoleErrors(ignorePatterns: string[] = []): Promise<void> {
    const errors = await new TestHelpers(this.page).checkConsoleErrors(ignorePatterns);
    expect(errors).toHaveLength(0);
  }
}