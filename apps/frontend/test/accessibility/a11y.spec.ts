import { test, expect } from '@playwright/test'
import AxeBuilder from '@axe-core/playwright'

test.describe('Accessibility Tests', () => {
  test('homepage has no accessibility violations', async ({ page }) => {
    await page.goto('/')
    
    // Wait for content to load
    await expect(page.getByRole('heading', { name: /vs code extension server/i })).toBeVisible()
    
    const accessibilityScanResults = await new AxeBuilder({ page }).analyze()
    
    expect(accessibilityScanResults.violations).toEqual([])
  })

  test('extension selection maintains accessibility', async ({ page }) => {
    await page.goto('/')
    
    // Select extension
    await page.getByText('VS Code TODOs').click()
    await expect(page.getByRole('button', { name: /download/i })).toBeVisible()
    
    const accessibilityScanResults = await new AxeBuilder({ page }).analyze()
    
    expect(accessibilityScanResults.violations).toEqual([])
  })

  test('keyboard navigation works correctly', async ({ page }) => {
    await page.goto('/')
    
    // Test tab navigation
    await page.keyboard.press('Tab')
    
    // Should be able to navigate through interactive elements
    const focusedElement = await page.evaluate(() => document.activeElement?.tagName)
    expect(['BUTTON', 'A', 'DIV', 'INPUT']).toContain(focusedElement)
    
    // Continue tabbing to test full navigation
    for (let i = 0; i < 5; i++) {
      await page.keyboard.press('Tab')
      const currentFocus = await page.evaluate(() => document.activeElement?.tagName)
      expect(currentFocus).toBeTruthy()
    }
  })

  test('screen reader compatibility', async ({ page }) => {
    await page.goto('/')
    
    // Check for proper heading structure
    const headings = await page.locator('h1, h2, h3, h4, h5, h6').all()
    expect(headings.length).toBeGreaterThan(0)
    
    // Check for alt text on images
    const images = await page.locator('img').all()
    for (const img of images) {
      const alt = await img.getAttribute('alt')
      expect(alt).toBeTruthy()
    }
    
    // Check for proper labels
    const inputs = await page.locator('input, select, textarea').all()
    for (const input of inputs) {
      const ariaLabel = await input.getAttribute('aria-label')
      const ariaLabelledBy = await input.getAttribute('aria-labelledby')
      const label = await page.locator(`label[for="${await input.getAttribute('id')}"]`).count()
      
      expect(ariaLabel || ariaLabelledBy || label > 0).toBeTruthy()
    }
  })

  test('color contrast meets WCAG guidelines', async ({ page }) => {
    await page.goto('/')
    
    // This would require more sophisticated color contrast checking
    // For now, we'll run axe which includes color contrast checks
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
      .analyze()
    
    // Filter for color contrast violations
    const colorContrastViolations = accessibilityScanResults.violations.filter(
      violation => violation.id === 'color-contrast'
    )
    
    expect(colorContrastViolations).toEqual([])
  })

  test('focus indicators are visible', async ({ page }) => {
    await page.goto('/')
    
    // Select extension first
    await page.getByText('VS Code TODOs').click()
    await expect(page.getByRole('button', { name: /download/i })).toBeVisible()
    
    // Focus on interactive elements and check visibility
    const interactiveElements = await page.locator('button, a, input, select, textarea, [tabindex]').all()
    
    for (const element of interactiveElements.slice(0, 5)) { // Test first 5 to avoid timeout
      await element.focus()
      
      // Check if focus is visible (this is a basic check)
      const isVisible = await element.isVisible()
      expect(isVisible).toBe(true)
      
      // Check for focus outline (basic test)
      const styles = await element.evaluate(el => {
        const computed = window.getComputedStyle(el, ':focus')
        return {
          outline: computed.outline,
          outlineWidth: computed.outlineWidth,
          boxShadow: computed.boxShadow
        }
      })
      
      // Should have some form of focus indicator
      const hasFocusIndicator = 
        styles.outline !== 'none' || 
        styles.outlineWidth !== '0px' || 
        styles.boxShadow !== 'none'
      
      expect(hasFocusIndicator).toBe(true)
    }
  })

  test('ARIA attributes are properly used', async ({ page }) => {
    await page.goto('/')
    
    // Select extension to show tabs
    await page.getByText('VS Code TODOs').click()
    await expect(page.getByRole('button', { name: /download/i })).toBeVisible()
    
    // Check for proper ARIA attributes on tabs
    const tabList = page.getByRole('tablist')
    await expect(tabList).toBeVisible()
    
    const tabs = await page.getByRole('tab').all()
    expect(tabs.length).toBeGreaterThan(0)
    
    for (const tab of tabs) {
      // Each tab should have proper ARIA attributes
      const ariaSelected = await tab.getAttribute('aria-selected')
      const ariaControls = await tab.getAttribute('aria-controls')
      
      expect(ariaSelected).toBeTruthy()
      expect(ariaControls).toBeTruthy()
    }
    
    // Check tab panels
    const tabPanels = await page.getByRole('tabpanel').all()
    expect(tabPanels.length).toBeGreaterThan(0)
    
    for (const panel of tabPanels) {
      const ariaLabelledBy = await panel.getAttribute('aria-labelledby')
      expect(ariaLabelledBy).toBeTruthy()
    }
  })

  test('semantic HTML structure', async ({ page }) => {
    await page.goto('/')
    
    // Check for proper semantic elements
    const main = page.locator('main')
    const nav = page.locator('nav')
    const header = page.locator('header')
    const section = page.locator('section')
    const article = page.locator('article')
    
    // Should have semantic structure (at least some semantic elements)
    const semanticCount = await Promise.all([
      main.count(),
      nav.count(),
      header.count(),
      section.count(),
      article.count()
    ]).then(counts => counts.reduce((sum, count) => sum + count, 0))
    
    // Should have some semantic elements or proper heading structure
    const headingCount = await page.locator('h1, h2, h3, h4, h5, h6').count()
    
    expect(semanticCount + headingCount).toBeGreaterThan(0)
  })

  test('mobile accessibility', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 })
    
    await page.goto('/')
    
    // Check accessibility on mobile
    const accessibilityScanResults = await new AxeBuilder({ page }).analyze()
    
    expect(accessibilityScanResults.violations).toEqual([])
    
    // Check touch target sizes
    const buttons = await page.locator('button').all()
    
    for (const button of buttons.slice(0, 3)) { // Test first 3 buttons
      const boundingBox = await button.boundingBox()
      
      if (boundingBox) {
        // WCAG recommends minimum 44x44px touch targets
        expect(boundingBox.width).toBeGreaterThanOrEqual(40) // Allow some tolerance
        expect(boundingBox.height).toBeGreaterThanOrEqual(40)
      }
    }
  })

  test('no accessibility violations in all states', async ({ page }) => {
    await page.goto('/')
    
    // Test different states
    const states = [
      async () => {
        // Default state
        await expect(page.getByText('Available Extensions')).toBeVisible()
      },
      async () => {
        // Extension selected state
        await page.getByText('VS Code TODOs').click()
        await expect(page.getByRole('button', { name: /download/i })).toBeVisible()
      },
      async () => {
        // Different tab selected
        await page.getByRole('tab', { name: /details/i }).click()
        await expect(page.getByText('Categories')).toBeVisible()
      }
    ]
    
    for (const setState of states) {
      await setState()
      
      const accessibilityScanResults = await new AxeBuilder({ page })
        .withTags(['wcag2a', 'wcag2aa'])
        .analyze()
      
      expect(accessibilityScanResults.violations).toEqual([])
    }
  })
})