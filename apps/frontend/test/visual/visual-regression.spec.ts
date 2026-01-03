import { test, expect } from '@playwright/test'

test.use({ 
  // Ensure consistent screenshots
  viewport: { width: 1280, height: 720 }
})

test.describe('Visual Regression Tests', () => {
  test('homepage layout matches baseline', async ({ page }) => {
    await page.goto('/')
    
    // Wait for content to load
    await expect(page.getByRole('heading', { name: /vs code extension server/i })).toBeVisible()
    await expect(page.getByText('Available Extensions')).toBeVisible()
    
    // Take full page screenshot
    await expect(page).toHaveScreenshot('homepage-full.png')
  })

  test('extension list matches baseline', async ({ page }) => {
    await page.goto('/')
    
    // Wait for extension to load
    await expect(page.getByText('VS Code TODOs')).toBeVisible()
    
    // Screenshot just the extension list
    const extensionList = page.locator('.space-y-2').first()
    await expect(extensionList).toHaveScreenshot('extension-list.png')
  })

  test('extension detail view matches baseline', async ({ page }) => {
    await page.goto('/')
    
    // Select extension
    await page.getByText('VS Code TODOs').click()
    await expect(page.getByRole('button', { name: /download/i })).toBeVisible()
    
    // Screenshot the detail panel
    const detailPanel = page.locator('.lg\\:col-span-2').first()
    await expect(detailPanel).toHaveScreenshot('extension-detail.png')
  })

  test('tabs display correctly', async ({ page }) => {
    await page.goto('/')
    
    // Select extension
    await page.getByText('VS Code TODOs').click()
    await expect(page.getByRole('button', { name: /download/i })).toBeVisible()
    
    const tabs = ['install', 'curl', 'details', 'keywords']
    
    for (const tabName of tabs) {
      await page.getByRole('tab', { name: new RegExp(tabName, 'i') }).click()
      
      // Wait for content to settle
      await page.waitForTimeout(100)
      
      // Screenshot the tab content
      const tabContent = page.locator('[role="tabpanel"]')
      await expect(tabContent).toHaveScreenshot(`tab-${tabName}.png`)
    }
  })

  test('mobile layout matches baseline', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 })
    
    await page.goto('/')
    
    // Wait for content to load
    await expect(page.getByRole('heading', { name: /vs code extension server/i })).toBeVisible()
    
    // Take mobile screenshot
    await expect(page).toHaveScreenshot('mobile-homepage.png')
    
    // Test mobile extension selection
    await page.getByText('VS Code TODOs').click()
    await expect(page.getByRole('button', { name: /download/i })).toBeVisible()
    
    await expect(page).toHaveScreenshot('mobile-extension-detail.png')
  })

  test('tablet layout matches baseline', async ({ page }) => {
    // Set tablet viewport
    await page.setViewportSize({ width: 768, height: 1024 })
    
    await page.goto('/')
    
    // Wait for content to load
    await expect(page.getByRole('heading', { name: /vs code extension server/i })).toBeVisible()
    
    // Take tablet screenshot
    await expect(page).toHaveScreenshot('tablet-layout.png')
  })

  test('empty state matches baseline', async ({ page }) => {
    await page.goto('/')
    
    // Wait for any content to load first
    await page.waitForTimeout(1000)
    
    // Look for empty state elements
    const emptyState = page.getByText('Select an Extension')
    if (await emptyState.isVisible()) {
      const emptyPanel = page.locator('.lg\\:col-span-2').first()
      await expect(emptyPanel).toHaveScreenshot('empty-state.png')
    }
  })

  test('hover states match baseline', async ({ page }) => {
    await page.goto('/')
    
    // Wait for extension to load
    await expect(page.getByText('VS Code TODOs')).toBeVisible()
    
    // Hover over extension item
    await page.getByText('VS Code TODOs').hover()
    
    // Screenshot the hovered extension
    const extensionItem = page.locator('.cursor-pointer').first()
    await expect(extensionItem).toHaveScreenshot('extension-hover.png')
    
    // Click to select and test button hover
    await page.getByText('VS Code TODOs').click()
    await expect(page.getByRole('button', { name: /download/i })).toBeVisible()
    
    // Hover over download button
    await page.getByRole('button', { name: /download/i }).hover()
    
    // Screenshot the hovered button
    const downloadButton = page.getByRole('button', { name: /download/i })
    await expect(downloadButton).toHaveScreenshot('download-button-hover.png')
  })

  test('focus states match baseline', async ({ page }) => {
    await page.goto('/')
    
    // Wait for content
    await expect(page.getByText('VS Code TODOs')).toBeVisible()
    
    // Focus on extension item using keyboard
    await page.keyboard.press('Tab')
    
    // If the extension item gets focus, screenshot it
    const focused = await page.evaluate(() => document.activeElement?.textContent?.includes('VS Code TODOs'))
    
    if (focused) {
      await expect(page.locator(':focus')).toHaveScreenshot('extension-focus.png')
    }
    
    // Test button focus
    await page.getByText('VS Code TODOs').click()
    await expect(page.getByRole('button', { name: /download/i })).toBeVisible()
    
    // Focus the download button
    await page.getByRole('button', { name: /download/i }).focus()
    await expect(page.getByRole('button', { name: /download/i })).toHaveScreenshot('button-focus.png')
  })

  test('dark mode compatibility', async ({ page }) => {
    // Add dark class to test dark mode (if implemented)
    await page.goto('/')
    
    // This assumes dark mode would be implemented
    await page.evaluate(() => {
      document.documentElement.classList.add('dark')
    })
    
    // Wait for style changes
    await page.waitForTimeout(200)
    
    await expect(page.getByRole('heading', { name: /vs code extension server/i })).toBeVisible()
    
    // Take dark mode screenshot
    await expect(page).toHaveScreenshot('dark-mode-homepage.png')
  })

  test('different content lengths', async ({ page }) => {
    await page.goto('/')
    
    // This would test with different extension descriptions/content lengths
    // For now, test the current content
    await expect(page.getByText('VS Code TODOs')).toBeVisible()
    
    await page.getByText('VS Code TODOs').click()
    await expect(page.getByRole('button', { name: /download/i })).toBeVisible()
    
    // Test the metadata display with varying content
    const metadataBlock = page.locator('code').first()
    await expect(metadataBlock).toHaveScreenshot('metadata-display.png')
  })
})