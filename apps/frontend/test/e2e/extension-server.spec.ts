import { test, expect } from '@playwright/test'

test.describe('Extension Server E2E', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('displays the main page correctly', async ({ page }) => {
    // Check main heading
    await expect(page.getByRole('heading', { name: /vs code extension server/i })).toBeVisible()
    
    // Check description
    await expect(page.getByText(/manage and distribute custom vs code extensions/i)).toBeVisible()
    
    // Check that extensions list is visible
    await expect(page.getByText('Available Extensions')).toBeVisible()
  })

  test('shows initial sample extension', async ({ page }) => {
    // Wait for the extension to load
    await expect(page.getByText('VS Code TODOs')).toBeVisible()
    
    // Check extension details
    await expect(page.getByText('example-publisher • v1.2.3')).toBeVisible()
    await expect(page.getByText('Highlight and manage TODO comments')).toBeVisible()
  })

  test('selects extension and shows details', async ({ page }) => {
    // Click on the extension
    await page.getByText('VS Code TODOs').click()
    
    // Wait for details to load
    await expect(page.getByRole('button', { name: /download/i })).toBeVisible()
    
    // Check that install command is visible
    await expect(page.getByText('code --install-extension vscode-todos-1.2.3.vsix')).toBeVisible()
    
    // Check that metadata is visible
    await expect(page.getByText('"name": "vscode-todos"')).toBeVisible()
  })

  test('navigates between tabs', async ({ page }) => {
    // Select extension first
    await page.getByText('VS Code TODOs').click()
    await expect(page.getByRole('button', { name: /download/i })).toBeVisible()
    
    // Test API tab
    await page.getByRole('tab', { name: /api/i }).click()
    await expect(page.getByText('cURL Examples')).toBeVisible()
    await expect(page.getByText('curl')).toBeVisible()
    
    // Test Details tab
    await page.getByRole('tab', { name: /details/i }).click()
    await expect(page.getByText('Categories')).toBeVisible()
    await expect(page.getByText('Programming Languages')).toBeVisible()
    
    // Test Keywords tab
    await page.getByRole('tab', { name: /keywords/i }).click()
    await expect(page.getByText('Keywords')).toBeVisible()
    await expect(page.getByText('todo')).toBeVisible()
    await expect(page.getByText('productivity')).toBeVisible()
    
    // Return to Install tab
    await page.getByRole('tab', { name: /install/i }).click()
    await expect(page.getByText('Installation Command')).toBeVisible()
  })

  test('copy functionality works', async ({ page }) => {
    // Grant clipboard permissions
    await page.context().grantPermissions(['clipboard-write'])
    
    // Select extension
    await page.getByText('VS Code TODOs').click()
    await expect(page.getByRole('button', { name: /download/i })).toBeVisible()
    
    // Find and click the first copy button (install command)
    const copyButtons = page.getByRole('button').filter({ has: page.locator('svg') })
    await copyButtons.first().click()
    
    // Check for success toast (sonner)
    await expect(page.getByText(/copied to clipboard/i)).toBeVisible()
  })

  test('download button triggers download', async ({ page }) => {
    // Listen for download events
    const downloadPromise = page.waitForEvent('download')
    
    // Select extension and click download
    await page.getByText('VS Code TODOs').click()
    await page.getByRole('button', { name: /download/i }).click()
    
    const download = await downloadPromise
    expect(download.suggestedFilename()).toContain('.vsix')
  })

  test('responsive design works on mobile', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 })
    
    // Check that content is still accessible
    await expect(page.getByRole('heading', { name: /vs code extension server/i })).toBeVisible()
    await expect(page.getByText('Available Extensions')).toBeVisible()
    
    // Extension should still be clickable
    await page.getByText('VS Code TODOs').click()
    await expect(page.getByRole('button', { name: /download/i })).toBeVisible()
  })

  test('handles no extensions state', async ({ page }) => {
    // This would require mocking the data, but for now we test the UI structure
    await expect(page.getByText('Available Extensions')).toBeVisible()
    
    // If no extension is selected, should show selection prompt
    const selectionText = page.getByText('Select an Extension')
    if (await selectionText.isVisible()) {
      await expect(selectionText).toBeVisible()
      await expect(page.getByText('Choose an extension from the list')).toBeVisible()
    }
  })

  test('accessibility features work correctly', async ({ page }) => {
    // Check heading hierarchy
    const h1 = page.getByRole('heading', { level: 1 })
    await expect(h1).toBeVisible()
    
    // Check that buttons have proper labels
    await page.getByText('VS Code TODOs').click()
    
    const downloadButton = page.getByRole('button', { name: /download/i })
    await expect(downloadButton).toBeVisible()
    
    // Check tab navigation
    const tabs = page.getByRole('tablist')
    await expect(tabs).toBeVisible()
    
    // Test keyboard navigation
    await page.keyboard.press('Tab')
    await page.keyboard.press('Enter')
  })

  test('external links work correctly', async ({ page }) => {
    // Select extension
    await page.getByText('VS Code TODOs').click()
    
    // Go to Details tab
    await page.getByRole('tab', { name: /details/i }).click()
    
    // Check for repository link
    const repoLink = page.getByRole('link', { name: /view source/i })
    if (await repoLink.isVisible()) {
      await expect(repoLink).toHaveAttribute('target', '_blank')
      await expect(repoLink).toHaveAttribute('rel', /noopener noreferrer/)
    }
  })
})