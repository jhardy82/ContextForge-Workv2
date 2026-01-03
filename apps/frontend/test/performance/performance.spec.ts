import { test, expect } from '@playwright/test'

test.describe('Performance Tests', () => {
  test('page loads within performance budget', async ({ page }) => {
    const startTime = Date.now()
    
    await page.goto('/')
    
    // Wait for main content to be visible
    await expect(page.getByRole('heading', { name: /vs code extension server/i })).toBeVisible()
    
    const loadTime = Date.now() - startTime
    
    // Should load within 2 seconds
    expect(loadTime).toBeLessThan(2000)
  })

  test('extension selection is responsive', async ({ page }) => {
    await page.goto('/')
    
    // Wait for extension to be available
    await expect(page.getByText('VS Code TODOs')).toBeVisible()
    
    const startTime = Date.now()
    
    // Click extension
    await page.getByText('VS Code TODOs').click()
    
    // Wait for details to appear
    await expect(page.getByRole('button', { name: /download/i })).toBeVisible()
    
    const responseTime = Date.now() - startTime
    
    // Should respond within 500ms
    expect(responseTime).toBeLessThan(500)
  })

  test('tab switching performance', async ({ page }) => {
    await page.goto('/')
    
    // Select extension
    await page.getByText('VS Code TODOs').click()
    await expect(page.getByRole('button', { name: /download/i })).toBeVisible()
    
    const tabs = ['api', 'details', 'keywords', 'install']
    
    for (const tabName of tabs) {
      const startTime = Date.now()
      
      await page.getByRole('tab', { name: new RegExp(tabName, 'i') }).click()
      
      // Wait for tab content to be visible
      await page.waitForTimeout(50) // Small delay to ensure content loads
      
      const switchTime = Date.now() - startTime
      
      // Tab switching should be nearly instant
      expect(switchTime).toBeLessThan(200)
    }
  })

  test('memory usage remains stable', async ({ page }) => {
    await page.goto('/')
    
    // Get initial memory usage
    const initialMetrics = await page.evaluate(() => {
      return (performance as any).memory ? {
        usedJSHeapSize: (performance as any).memory.usedJSHeapSize,
        totalJSHeapSize: (performance as any).memory.totalJSHeapSize
      } : null
    })
    
    if (!initialMetrics) {
      test.skip()
      return
    }
    
    // Perform multiple interactions
    for (let i = 0; i < 5; i++) {
      await page.getByText('VS Code TODOs').click()
      await page.getByRole('tab', { name: /api/i }).click()
      await page.getByRole('tab', { name: /details/i }).click()
      await page.getByRole('tab', { name: /install/i }).click()
      await page.waitForTimeout(100)
    }
    
    // Force garbage collection if available
    await page.evaluate(() => {
      if (window.gc) {
        window.gc()
      }
    })
    
    // Get final memory usage
    const finalMetrics = await page.evaluate(() => {
      return {
        usedJSHeapSize: (performance as any).memory.usedJSHeapSize,
        totalJSHeapSize: (performance as any).memory.totalJSHeapSize
      }
    })
    
    // Memory shouldn't increase by more than 50%
    const memoryIncrease = (finalMetrics.usedJSHeapSize - initialMetrics.usedJSHeapSize) / initialMetrics.usedJSHeapSize
    expect(memoryIncrease).toBeLessThan(0.5)
  })

  test('lighthouse performance score', async ({ page }) => {
    // This would require lighthouse integration
    // For now, we'll test basic performance metrics
    
    await page.goto('/')
    
    // Measure Core Web Vitals
    const vitals = await page.evaluate(() => {
      return new Promise((resolve) => {
        const observer = new PerformanceObserver((list) => {
          const entries = list.getEntries()
          const vitals: Record<string, number> = {}
          
          entries.forEach((entry) => {
            if (entry.name === 'first-contentful-paint') {
              vitals.fcp = entry.startTime
            }
            if (entry.name === 'largest-contentful-paint') {
              vitals.lcp = entry.startTime
            }
          })
          
          resolve(vitals)
        })
        
        observer.observe({ entryTypes: ['paint', 'largest-contentful-paint'] })
        
        // Fallback timeout
        setTimeout(() => resolve({}), 5000)
      })
    })
    
    // Basic performance assertions
    if ((vitals as any).fcp) {
      expect((vitals as any).fcp).toBeLessThan(2000) // FCP under 2s
    }
    
    if ((vitals as any).lcp) {
      expect((vitals as any).lcp).toBeLessThan(2500) // LCP under 2.5s
    }
  })

  test('handles large datasets efficiently', async ({ page }) => {
    // This would test with a large number of extensions
    // For now, we test the current implementation doesn't degrade
    
    await page.goto('/')
    
    const startTime = Date.now()
    
    // Perform rapid interactions
    for (let i = 0; i < 10; i++) {
      await page.getByText('VS Code TODOs').click()
      if (i % 2 === 0) {
        await page.getByRole('tab', { name: /api/i }).click()
      } else {
        await page.getByRole('tab', { name: /details/i }).click()
      }
    }
    
    const totalTime = Date.now() - startTime
    
    // Should handle rapid interactions efficiently
    expect(totalTime).toBeLessThan(3000)
  })
})