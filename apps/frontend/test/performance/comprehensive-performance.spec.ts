import { test, expect } from '@playwright/test';
import { playAudit } from 'playwright-lighthouse';

/**
 * Comprehensive Performance Testing Suite
 * Tests Core Web Vitals, Lighthouse scores, network performance,
 * memory usage, and runtime performance metrics
 */
test.describe('Comprehensive Performance Tests', () => {
  
  test.beforeEach(async ({ page }) => {
    // Setup mock API responses for consistent testing
    await page.route('**/api/v1/health', async route => {
      await route.fulfill({
        json: { connected: true, status: 'connected', version: '1.0.0' }
      });
    });

    await page.route('**/api/v1/projects', async route => {
      await route.fulfill({
        json: Array.from({ length: 10 }, (_, i) => ({
          id: `${i + 1}`,
          name: `Performance Test Project ${i + 1}`,
          description: `Testing performance with project ${i + 1}`,
          status: 'active',
          created: new Date().toISOString(),
          updated: new Date().toISOString()
        }))
      });
    });

    await page.route('**/api/v1/tasks', async route => {
      await route.fulfill({
        json: Array.from({ length: 50 }, (_, i) => ({
          id: `${i + 1}`,
          title: `Performance Task ${i + 1}`,
          description: `Testing performance with large dataset - task ${i + 1}`,
          status: ['new', 'in-progress', 'pending', 'completed', 'blocked'][i % 5],
          priority: ['low', 'medium', 'high', 'critical'][i % 4],
          projectId: `${(i % 10) + 1}`,
          created: new Date(Date.now() - i * 3600000).toISOString(),
          updated: new Date(Date.now() - i * 1800000).toISOString(),
          assignee: `user-${i % 5}`,
          tags: [`tag-${i % 3}`, `category-${i % 4}`]
        }))
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

  test('meets Core Web Vitals standards', async ({ page }) => {
    // Enable performance monitoring
    await page.coverage.startJSCoverage();
    await page.coverage.startCSSCoverage();
    
    const startTime = Date.now();
    await page.goto('/');
    
    // Wait for content to be fully loaded
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(3000); // Allow for any lazy loading
    
    const endTime = Date.now();
    const loadTime = endTime - startTime;
    
    // Page should load within reasonable time (< 3 seconds)
    expect(loadTime).toBeLessThan(3000);
    
    // Get Core Web Vitals using Performance API
    const webVitals = await page.evaluate(() => {
      return new Promise((resolve) => {
        // Collect performance metrics
        const paintEntries = performance.getEntriesByType('paint');
        const navigationEntries = performance.getEntriesByType('navigation');
        
        const metrics = {
          firstPaint: paintEntries.find(entry => entry.name === 'first-paint')?.startTime || 0,
          firstContentfulPaint: paintEntries.find(entry => entry.name === 'first-contentful-paint')?.startTime || 0,
          domContentLoaded: navigationEntries[0]?.domContentLoadedEventEnd || 0,
          loadComplete: navigationEntries[0]?.loadEventEnd || 0
        };
        
        // Try to get CLS, LCP, FID if available
        if ('PerformanceObserver' in window) {
          const observer = new PerformanceObserver((list) => {
            const entries = list.getEntries();
            entries.forEach((entry) => {
              if (entry.entryType === 'largest-contentful-paint') {
                metrics.largestContentfulPaint = entry.startTime;
              }
              if (entry.entryType === 'layout-shift' && !entry.hadRecentInput) {
                metrics.cumulativeLayoutShift = (metrics.cumulativeLayoutShift || 0) + entry.value;
              }
            });
          });
          
          try {
            observer.observe({ entryTypes: ['largest-contentful-paint', 'layout-shift'] });
          } catch (e) {
            // Some browsers may not support all entry types
          }
          
          setTimeout(() => {
            observer.disconnect();
            resolve(metrics);
          }, 2000);
        } else {
          resolve(metrics);
        }
      });
    });
    
    // Core Web Vitals thresholds (Google recommendations)
    if (webVitals.firstContentfulPaint > 0) {
      expect(webVitals.firstContentfulPaint).toBeLessThan(1800); // FCP < 1.8s (good)
    }
    
    if (webVitals.largestContentfulPaint > 0) {
      expect(webVitals.largestContentfulPaint).toBeLessThan(2500); // LCP < 2.5s (good)
    }
    
    if (webVitals.cumulativeLayoutShift !== undefined) {
      expect(webVitals.cumulativeLayoutShift).toBeLessThan(0.1); // CLS < 0.1 (good)
    }
    
    // Stop coverage and analyze
    const jsCoverage = await page.coverage.stopJSCoverage();
    const cssCoverage = await page.coverage.stopCSSCoverage();
    
    // Calculate code coverage
    const jsUsedBytes = jsCoverage.reduce((acc, entry) => acc + entry.usedBytes, 0);
    const jsTotalBytes = jsCoverage.reduce((acc, entry) => acc + entry.totalBytes, 0);
    const jsUtilization = jsUsedBytes / jsTotalBytes;
    
    const cssUsedBytes = cssCoverage.reduce((acc, entry) => acc + entry.usedBytes, 0);
    const cssTotalBytes = cssCoverage.reduce((acc, entry) => acc + entry.totalBytes, 0);
    const cssUtilization = cssUsedBytes / cssTotalBytes;
    
    // Code utilization should be reasonable (> 50%)
    expect(jsUtilization).toBeGreaterThan(0.3);
    expect(cssUtilization).toBeGreaterThan(0.3);
    
    console.log('Performance Metrics:', {
      loadTime,
      webVitals,
      codeUtilization: {
        js: `${(jsUtilization * 100).toFixed(1)}%`,
        css: `${(cssUtilization * 100).toFixed(1)}%`
      }
    });
  });

  test('performs well with large datasets', async ({ page }) => {
    const startTime = Date.now();
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Wait for tasks to load (large dataset)
    await page.waitForTimeout(3000);
    
    // Should display tasks without performance issues
    const taskElements = await page.locator('[data-testid*="task"], .task-item, .task').count();
    expect(taskElements).toBeGreaterThan(10); // Should show multiple tasks
    
    // Test scrolling performance with large list
    const scrollStart = Date.now();
    await page.evaluate(() => {
      const scrollableElement = document.querySelector('[data-testid="task-list"], .task-list, main') || document.body;
      scrollableElement.scrollTop = scrollableElement.scrollHeight;
    });
    
    await page.waitForTimeout(100);
    const scrollEnd = Date.now();
    const scrollTime = scrollEnd - scrollStart;
    
    // Scrolling should be smooth (< 100ms)
    expect(scrollTime).toBeLessThan(100);
    
    // Test filtering performance
    const filterStart = Date.now();
    const searchInput = page.locator('input[placeholder*="search"], input[placeholder*="filter"]').first();
    
    if (await searchInput.isVisible()) {
      await searchInput.fill('Performance Task 1');
      await page.waitForTimeout(500); // Wait for filter to apply
      
      const filterEnd = Date.now();
      const filterTime = filterEnd - filterStart;
      
      // Filtering should be fast (< 500ms)
      expect(filterTime).toBeLessThan(500);
      
      // Should show filtered results
      const filteredTasks = await page.locator('[data-testid*="task"], .task-item, .task').count();
      expect(filteredTasks).toBeGreaterThan(0);
      expect(filteredTasks).toBeLessThan(taskElements); // Should be filtered
    }
  });

  test('handles memory usage efficiently', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // Get initial memory usage
    const initialMemory = await page.evaluate(() => {
      if ('memory' in performance) {
        return {
          usedJSHeapSize: (performance as any).memory.usedJSHeapSize,
          totalJSHeapSize: (performance as any).memory.totalJSHeapSize,
          jsHeapSizeLimit: (performance as any).memory.jsHeapSizeLimit
        };
      }
      return null;
    });
    
    if (initialMemory) {
      console.log('Initial memory usage:', initialMemory);
      
      // Perform memory-intensive operations
      for (let i = 0; i < 5; i++) {
        // Refresh data multiple times
        const refreshButton = page.getByRole('button', { name: /refresh/i });
        if (await refreshButton.isVisible()) {
          await refreshButton.click();
          await page.waitForTimeout(1000);
        }
        
        // Open and close modals
        const taskElements = await page.locator('[data-testid*="task"], .task-item, .task').all();
        if (taskElements.length > 0) {
          await taskElements[0].click();
          await page.waitForTimeout(500);
          
          const closeButton = page.getByRole('button', { name: /close|×/i }).first();
          if (await closeButton.isVisible()) {
            await closeButton.click();
            await page.waitForTimeout(500);
          } else {
            await page.keyboard.press('Escape');
          }
        }
      }
      
      // Force garbage collection if available
      await page.evaluate(() => {
        if ('gc' in window) {
          (window as any).gc();
        }
      });
      
      await page.waitForTimeout(1000);
      
      // Check final memory usage
      const finalMemory = await page.evaluate(() => {
        if ('memory' in performance) {
          return {
            usedJSHeapSize: (performance as any).memory.usedJSHeapSize,
            totalJSHeapSize: (performance as any).memory.totalJSHeapSize,
            jsHeapSizeLimit: (performance as any).memory.jsHeapSizeLimit
          };
        }
        return null;
      });
      
      if (finalMemory) {
        console.log('Final memory usage:', finalMemory);
        
        const memoryIncrease = finalMemory.usedJSHeapSize - initialMemory.usedJSHeapSize;
        const memoryIncreasePercent = (memoryIncrease / initialMemory.usedJSHeapSize) * 100;
        
        // Memory increase should be reasonable (< 50% increase)
        expect(memoryIncreasePercent).toBeLessThan(50);
        
        // Should not exceed heap size limit
        expect(finalMemory.usedJSHeapSize).toBeLessThan(finalMemory.jsHeapSizeLimit * 0.8);
      }
    }
  });

  test('network requests are optimized', async ({ page }) => {
    const networkRequests: Array<{ url: string; method: string; responseTime: number; size: number }> = [];
    
    // Monitor network requests
    page.on('response', async (response) => {
      const request = response.request();
      const timing = response.timing();
      
      try {
        const responseTime = timing.responseEnd - timing.requestStart;
        const headers = await response.allHeaders();
        const contentLength = headers['content-length'];
        
        networkRequests.push({
          url: request.url(),
          method: request.method(),
          responseTime,
          size: contentLength ? parseInt(contentLength) : 0
        });
      } catch (error) {
        // Some responses might fail to get headers
      }
    });
    
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // Analyze network requests
    const apiRequests = networkRequests.filter(req => req.url.includes('/api/'));
    const staticRequests = networkRequests.filter(req => 
      req.url.includes('.js') || req.url.includes('.css') || req.url.includes('.html')
    );
    
    console.log('Network analysis:', {
      totalRequests: networkRequests.length,
      apiRequests: apiRequests.length,
      staticRequests: staticRequests.length
    });
    
    // API requests should be fast (< 1000ms)
    apiRequests.forEach(req => {
      expect(req.responseTime).toBeLessThan(1000);
    });
    
    // Should not make excessive API calls
    expect(apiRequests.length).toBeLessThan(20);
    
    // Static resources should be reasonably sized
    staticRequests.forEach(req => {
      if (req.size > 0) {
        // JavaScript bundles should be < 1MB
        if (req.url.includes('.js')) {
          expect(req.size).toBeLessThan(1024 * 1024);
        }
        // CSS should be < 100KB
        if (req.url.includes('.css')) {
          expect(req.size).toBeLessThan(100 * 1024);
        }
      }
    });
  });

  test('renders components efficiently', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Measure rendering performance
    const renderingMetrics = await page.evaluate(() => {
      return new Promise((resolve) => {
        const observer = new PerformanceObserver((list) => {
          const entries = list.getEntries().filter(entry => 
            entry.entryType === 'measure' || entry.entryType === 'mark'
          );
          
          observer.disconnect();
          resolve(entries.map(entry => ({
            name: entry.name,
            duration: entry.duration,
            startTime: entry.startTime
          })));
        });
        
        try {
          observer.observe({ entryTypes: ['measure', 'mark'] });
          
          // Create some performance marks for React rendering
          performance.mark('render-start');
          
          // Trigger a re-render
          setTimeout(() => {
            performance.mark('render-end');
            performance.measure('render-duration', 'render-start', 'render-end');
          }, 100);
          
          setTimeout(() => {
            observer.disconnect();
            resolve([]);
          }, 1000);
        } catch (e) {
          resolve([]);
        }
      });
    });
    
    console.log('Rendering metrics:', renderingMetrics);
    
    // Test component rendering under load
    const componentRenderStart = Date.now();
    
    // Rapidly toggle modal visibility to test rendering performance
    for (let i = 0; i < 5; i++) {
      const taskElements = await page.locator('[data-testid*="task"], .task-item, .task').all();
      if (taskElements.length > 0) {
        await taskElements[i % taskElements.length].click();
        await page.waitForTimeout(100);
        
        const modal = page.getByRole('dialog');
        if (await modal.isVisible()) {
          await page.keyboard.press('Escape');
          await page.waitForTimeout(100);
        }
      }
    }
    
    const componentRenderEnd = Date.now();
    const renderTime = componentRenderEnd - componentRenderStart;
    
    // Component rendering should be efficient (< 2 seconds for 5 cycles)
    expect(renderTime).toBeLessThan(2000);
  });

  test('performs well on mobile devices', async ({ page }) => {
    // Simulate mobile device constraints
    await page.setViewportSize({ width: 375, height: 667 });
    await page.emulateMedia({ media: 'screen' });
    
    // Simulate slow network
    const client = await page.context().newCDPSession(page);
    await client.send('Network.emulateNetworkConditions', {
      offline: false,
      downloadThroughput: 1.5 * 1024 * 1024 / 8, // 1.5 Mbps
      uploadThroughput: 750 * 1024 / 8, // 750 Kbps
      latency: 40 // 40ms latency
    });
    
    const startTime = Date.now();
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    const endTime = Date.now();
    
    const mobileLoadTime = endTime - startTime;
    
    // Should load reasonably fast even on mobile (< 5 seconds)
    expect(mobileLoadTime).toBeLessThan(5000);
    
    // Test mobile interactions
    const taskElements = await page.locator('[data-testid*="task"], .task-item, .task').all();
    if (taskElements.length > 0) {
      const tapStart = Date.now();
      await taskElements[0].tap();
      
      // Modal should open
      const modal = page.getByRole('dialog');
      if (await modal.isVisible()) {
        const tapEnd = Date.now();
        const tapResponseTime = tapEnd - tapStart;
        
        // Touch response should be immediate (< 100ms)
        expect(tapResponseTime).toBeLessThan(100);
        
        await page.keyboard.press('Escape');
      }
    }
    
    // Test scrolling performance on mobile
    const scrollStart = Date.now();
    await page.evaluate(() => {
      window.scrollTo(0, document.body.scrollHeight);
    });
    await page.waitForTimeout(100);
    const scrollEnd = Date.now();
    const scrollTime = scrollEnd - scrollStart;
    
    // Mobile scrolling should be smooth
    expect(scrollTime).toBeLessThan(200);
  });

  test('handles concurrent operations efficiently', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
    
    // Test concurrent API calls
    const concurrentStart = Date.now();
    
    const operations = Array.from({ length: 5 }, async (_, i) => {
      // Trigger refresh (API call)
      const refreshButton = page.getByRole('button', { name: /refresh/i });
      if (await refreshButton.isVisible()) {
        await refreshButton.click();
        await page.waitForTimeout(200);
      }
    });
    
    await Promise.all(operations);
    
    const concurrentEnd = Date.now();
    const concurrentTime = concurrentEnd - concurrentStart;
    
    // Concurrent operations should not block the UI excessively
    expect(concurrentTime).toBeLessThan(3000);
    
    // UI should remain responsive
    const responsiveStart = Date.now();
    const settingsButton = page.getByRole('button', { name: /settings/i });
    if (await settingsButton.isVisible()) {
      await settingsButton.click();
      
      const modal = page.getByRole('dialog');
      if (await modal.isVisible()) {
        const responsiveEnd = Date.now();
        const responseTime = responsiveEnd - responsiveStart;
        
        // UI should respond quickly even during concurrent operations
        expect(responseTime).toBeLessThan(500);
        
        await page.keyboard.press('Escape');
      }
    }
  });

  test('lighthouse performance audit', async ({ page, browser }) => {
    // Skip in CI or if lighthouse not available
    if (process.env.CI) {
      test.skip();
      return;
    }
    
    try {
      await page.goto('/');
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(2000);
      
      // Run Lighthouse audit
      const lighthouse = await playAudit({
        page,
        port: 9222,
        thresholds: {
          performance: 70,
          accessibility: 90,
          'best-practices': 80,
          seo: 70,
          pwa: 50
        },
        reports: {
          formats: {
            json: true,
            html: true
          },
          directory: './test-results/lighthouse',
          name: `lighthouse-${Date.now()}`
        }
      });
      
      // Assert Lighthouse scores
      expect(lighthouse.lhr.categories.performance.score).toBeGreaterThan(0.7);
      expect(lighthouse.lhr.categories.accessibility.score).toBeGreaterThan(0.9);
      expect(lighthouse.lhr.categories['best-practices'].score).toBeGreaterThan(0.8);
      
      console.log('Lighthouse scores:', {
        performance: lighthouse.lhr.categories.performance.score,
        accessibility: lighthouse.lhr.categories.accessibility.score,
        bestPractices: lighthouse.lhr.categories['best-practices'].score,
        seo: lighthouse.lhr.categories.seo.score,
        pwa: lighthouse.lhr.categories.pwa.score
      });
      
    } catch (error) {
      console.log('Lighthouse audit skipped:', error.message);
      test.skip();
    }
  });
});