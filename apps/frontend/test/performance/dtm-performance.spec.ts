import { test, expect } from '@playwright/test';

/**
 * DTM Performance Tests
 * Tests application performance metrics and loading times
 */
test.describe('DTM Performance', () => {
  test.beforeEach(async ({ page }) => {
    // Mock API responses with realistic delays
    await page.route('**/api/v1/health', async route => {
      await new Promise(resolve => setTimeout(resolve, 100)); // 100ms delay
      await route.fulfill({
        json: { version: '1.0.0', uptime: '24 hours' }
      });
    });

    await page.route('**/api/v1/projects', async route => {
      await new Promise(resolve => setTimeout(resolve, 200)); // 200ms delay
      await route.fulfill({
        json: Array.from({ length: 50 }, (_, i) => ({
          id: `P-PERF-${i.toString().padStart(3, '0')}`,
          name: `Performance Test Project ${i + 1}`,
          description: `Project ${i + 1} for performance testing`,
          status: i % 3 === 0 ? 'active' : i % 3 === 1 ? 'completed' : 'inactive',
          created_at: new Date(Date.now() - i * 86400000).toISOString()
        }))
      });
    });

    await page.route('**/api/v1/tasks', async route => {
      await new Promise(resolve => setTimeout(resolve, 300)); // 300ms delay
      await route.fulfill({
        json: Array.from({ length: 200 }, (_, i) => ({
          id: `T-PERF-${i.toString().padStart(3, '0')}`,
          title: `Performance Test Task ${i + 1}`,
          description: `Task ${i + 1} for performance testing with detailed description that is quite long and contains multiple sentences to simulate real-world task descriptions.`,
          status: ['new', 'in_progress', 'pending', 'completed', 'blocked'][i % 5],
          priority: ['low', 'medium', 'high', 'critical'][i % 4],
          shape: ['Triangle', 'Circle', 'Spiral', 'Pentagon', 'Fractal'][i % 5],
          project_id: `P-PERF-${Math.floor(i / 4).toString().padStart(3, '0')}`,
          created_at: new Date(Date.now() - i * 3600000).toISOString(),
          updated_at: new Date(Date.now() - i * 1800000).toISOString()
        }))
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
  });

  test('page load performance is acceptable', async ({ page }) => {
    const startTime = Date.now();
    
    await page.goto('/');
    
    // Wait for main content to be visible
    await page.waitForSelector('h1');
    
    const loadTime = Date.now() - startTime;
    
    // Page should load within 3 seconds
    expect(loadTime).toBeLessThan(3000);
    
    console.log(`Page load time: ${loadTime}ms`);
  });

  test('API data loading performance', async ({ page }) => {
    await page.goto('/');
    
    const startTime = Date.now();
    
    // Wait for all data to load
    await page.waitForTimeout(1000); // Wait for API calls to complete
    await page.waitForSelector('[data-testid="task-tree"]', { timeout: 10000 });
    
    const dataLoadTime = Date.now() - startTime;
    
    // Data should load within 5 seconds even with 200 tasks
    expect(dataLoadTime).toBeLessThan(5000);
    
    console.log(`Data load time: ${dataLoadTime}ms`);
  });

  test('UI responsiveness during data loading', async ({ page }) => {
    await page.goto('/');
    
    // Measure time to first interaction
    const startTime = Date.now();
    
    // Wait for first interactive element
    await page.waitForSelector('button:not([disabled])');
    
    const timeToInteractive = Date.now() - startTime;
    
    // Should be interactive within 2 seconds
    expect(timeToInteractive).toBeLessThan(2000);
    
    console.log(`Time to interactive: ${timeToInteractive}ms`);
  });

  test('task modal opening performance', async ({ page }) => {
    await page.goto('/');
    await page.waitForTimeout(2000);
    
    const startTime = Date.now();
    
    // Click on first task
    await page.getByText('Performance Test Task 1').click();
    
    // Wait for modal to be fully visible
    await page.waitForSelector('[role="dialog"]');
    
    const modalOpenTime = Date.now() - startTime;
    
    // Modal should open within 500ms
    expect(modalOpenTime).toBeLessThan(500);
    
    console.log(`Modal open time: ${modalOpenTime}ms`);
  });

  test('large dataset rendering performance', async ({ page }) => {
    await page.goto('/');
    
    const startTime = Date.now();
    
    // Wait for all tasks to be rendered
    await page.waitForTimeout(3000);
    
    // Count rendered tasks
    const taskCount = await page.locator('[data-testid="task-item"]').count();
    
    const renderTime = Date.now() - startTime;
    const renderTimePerTask = renderTime / taskCount;
    
    // Should render tasks efficiently
    expect(renderTimePerTask).toBeLessThan(10); // Less than 10ms per task
    expect(taskCount).toBeGreaterThan(100); // Should handle large datasets
    
    console.log(`Rendered ${taskCount} tasks in ${renderTime}ms (${renderTimePerTask.toFixed(2)}ms per task)`);
  });

  test('memory usage during navigation', async ({ page }) => {
    await page.goto('/');
    await page.waitForTimeout(2000);
    
    // Get initial memory usage
    const initialMemory = await page.evaluate(() => {
      return (performance as any).memory ? {
        usedJSHeapSize: (performance as any).memory.usedJSHeapSize,
        totalJSHeapSize: (performance as any).memory.totalJSHeapSize
      } : null;
    });
    
    // Perform multiple navigation actions
    for (let i = 0; i < 10; i++) {
      await page.getByText(`Performance Test Task ${i + 1}`).click();
      await page.waitForSelector('[role="dialog"]');
      await page.keyboard.press('Escape');
      await page.waitForTimeout(100);
    }
    
    // Get final memory usage
    const finalMemory = await page.evaluate(() => {
      return (performance as any).memory ? {
        usedJSHeapSize: (performance as any).memory.usedJSHeapSize,
        totalJSHeapSize: (performance as any).memory.totalJSHeapSize
      } : null;
    });
    
    if (initialMemory && finalMemory) {
      const memoryIncrease = finalMemory.usedJSHeapSize - initialMemory.usedJSHeapSize;
      const memoryIncreasePercent = (memoryIncrease / initialMemory.usedJSHeapSize) * 100;
      
      // Memory increase should be reasonable (less than 50% for this test)
      expect(memoryIncreasePercent).toBeLessThan(50);
      
      console.log(`Memory increase: ${memoryIncrease} bytes (${memoryIncreasePercent.toFixed(2)}%)`);
    }
  });

  test('network request optimization', async ({ page }) => {
    const requests: any[] = [];
    
    page.on('request', request => {
      requests.push({
        url: request.url(),
        method: request.method(),
        timestamp: Date.now()
      });
    });
    
    await page.goto('/');
    await page.waitForTimeout(3000);
    
    const apiRequests = requests.filter(req => req.url.includes('/api/'));
    
    // Should not make excessive API requests
    expect(apiRequests.length).toBeLessThan(10);
    
    // Check for duplicate requests
    const uniqueUrls = new Set(apiRequests.map(req => req.url));
    const duplicateRequests = apiRequests.length - uniqueUrls.size;
    
    expect(duplicateRequests).toBeLessThan(3); // Allow some retries
    
    console.log(`Made ${apiRequests.length} API requests (${duplicateRequests} duplicates)`);
  });

  test('scroll performance with large dataset', async ({ page }) => {
    await page.goto('/');
    await page.waitForTimeout(3000);
    
    const startTime = Date.now();
    
    // Perform scroll operations
    for (let i = 0; i < 10; i++) {
      await page.mouse.wheel(0, 500);
      await page.waitForTimeout(50);
    }
    
    const scrollTime = Date.now() - startTime;
    
    // Scrolling should be smooth (less than 1 second for 10 scroll operations)
    expect(scrollTime).toBeLessThan(1000);
    
    console.log(`Scroll performance: ${scrollTime}ms for 10 scroll operations`);
  });

  test('search/filter performance', async ({ page }) => {
    await page.goto('/');
    await page.waitForTimeout(3000);
    
    const searchInput = page.getByPlaceholder(/search|filter/i);
    
    if (await searchInput.isVisible()) {
      const startTime = Date.now();
      
      // Type search query
      await searchInput.fill('Performance Test Task 1');
      
      // Wait for filter results
      await page.waitForTimeout(500);
      
      const filterTime = Date.now() - startTime;
      
      // Filtering should be fast (less than 500ms)
      expect(filterTime).toBeLessThan(500);
      
      console.log(`Search/filter time: ${filterTime}ms`);
    }
  });

  test('concurrent operations performance', async ({ page }) => {
    await page.goto('/');
    await page.waitForTimeout(2000);
    
    const startTime = Date.now();
    
    // Perform multiple concurrent operations
    const operations = [
      page.getByRole('button', { name: /refresh/i }).click(),
      page.getByRole('button', { name: /settings/i }).click(),
      page.getByText('Performance Test Task 1').click()
    ];
    
    await Promise.all(operations);
    
    const concurrentTime = Date.now() - startTime;
    
    // Concurrent operations should complete reasonably fast
    expect(concurrentTime).toBeLessThan(2000);
    
    console.log(`Concurrent operations time: ${concurrentTime}ms`);
  });

  test('bundle size impact', async ({ page }) => {
    // Navigate and measure resource loading
    const responses: any[] = [];
    
    page.on('response', response => {
      if (response.url().includes('.js') || response.url().includes('.css')) {
        responses.push({
          url: response.url(),
          size: response.headers()['content-length'] || 'unknown'
        });
      }
    });
    
    await page.goto('/');
    await page.waitForTimeout(2000);
    
    const totalBundleSize = responses.reduce((total, response) => {
      const size = parseInt(response.size) || 0;
      return total + size;
    }, 0);
    
    // Bundle size should be reasonable (less than 2MB total)
    expect(totalBundleSize).toBeLessThan(2 * 1024 * 1024);
    
    console.log(`Total bundle size: ${totalBundleSize} bytes`);
  });

  test('layout shift measurement', async ({ page }) => {
    await page.goto('/');
    
    // Measure Cumulative Layout Shift (CLS)
    const cls = await page.evaluate(() => {
      return new Promise((resolve) => {
        let clsValue = 0;
        let clsEntries: any[] = [];
        
        const observer = new PerformanceObserver((entryList) => {
          for (const entry of entryList.getEntries()) {
            if (!(entry as any).hadRecentInput) {
              clsValue += (entry as any).value;
              clsEntries.push(entry);
            }
          }
        });
        
        observer.observe({ type: 'layout-shift', buffered: true });
        
        // Wait 3 seconds to collect layout shifts
        setTimeout(() => {
          observer.disconnect();
          resolve({ value: clsValue, entries: clsEntries.length });
        }, 3000);
      });
    });
    
    // CLS should be low (less than 0.1 is good, less than 0.25 is acceptable)
    expect((cls as any).value).toBeLessThan(0.25);
    
    console.log(`Cumulative Layout Shift: ${(cls as any).value} (${(cls as any).entries} shifts)`);
  });

  test('First Contentful Paint (FCP)', async ({ page }) => {
    await page.goto('/');
    
    const fcp = await page.evaluate(() => {
      return new Promise((resolve) => {
        const observer = new PerformanceObserver((entryList) => {
          for (const entry of entryList.getEntries()) {
            if (entry.name === 'first-contentful-paint') {
              resolve(entry.startTime);
            }
          }
        });
        
        observer.observe({ type: 'paint', buffered: true });
        
        // Fallback timeout
        setTimeout(() => resolve(null), 5000);
      });
    });
    
    if (fcp) {
      // FCP should be fast (less than 2 seconds)
      expect(fcp as number).toBeLessThan(2000);
      console.log(`First Contentful Paint: ${fcp}ms`);
    }
  });

  test('auto-refresh performance impact', async ({ page }) => {
    await page.goto('/');
    await page.waitForTimeout(2000);
    
    // Enable auto-refresh
    await page.getByRole('button', { name: /settings/i }).click();
    const autoRefreshToggle = page.getByLabel(/auto.?refresh/i);
    if (await autoRefreshToggle.isVisible() && !(await autoRefreshToggle.isChecked())) {
      await autoRefreshToggle.check();
    }
    await page.keyboard.press('Escape');
    
    const startTime = Date.now();
    let requestCount = 0;
    
    page.on('request', request => {
      if (request.url().includes('/api/')) {
        requestCount++;
      }
    });
    
    // Wait for one auto-refresh cycle (30+ seconds)
    await page.waitForTimeout(35000);
    
    const elapsedTime = Date.now() - startTime;
    
    // Should not make excessive requests during auto-refresh
    const requestsPerSecond = requestCount / (elapsedTime / 1000);
    expect(requestsPerSecond).toBeLessThan(1); // Less than 1 request per second on average
    
    console.log(`Auto-refresh: ${requestCount} requests in ${elapsedTime}ms (${requestsPerSecond.toFixed(2)} req/s)`);
  });
});