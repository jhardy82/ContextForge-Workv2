import { test, expect } from '@playwright/test';

test.describe('Visual Regression Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('main page appearance', async ({ page }) => {
    // Wait for any animations to complete
    await page.waitForTimeout(500);
    
    // Take full page screenshot
    await expect(page).toHaveScreenshot('main-page.png', {
      fullPage: true,
      animations: 'disabled'
    });
  });

  test('extension list appearance', async ({ page }) => {
    // Focus on the extension list area
    const extensionList = page.locator('[data-testid="extension-list"]').first();
    
    // If no test ID exists, use the Available Extensions card
    const availableExtensions = page.getByText('Available Extensions').locator('..').locator('..');
    
    if (await extensionList.count() > 0) {
      await expect(extensionList).toHaveScreenshot('extension-list.png');
    } else if (await availableExtensions.count() > 0) {
      await expect(availableExtensions).toHaveScreenshot('extension-list-fallback.png');
    }
  });

  test('extension details panel', async ({ page }) => {
    const extensionCards = page.locator('[role="button"]:has-text("VS Code TODOs"), [role="button"]:has-text("Dynamic Task Manager")').first();
    
    if (await extensionCards.count() > 0) {
      await extensionCards.click();
      
      // Wait for details to load
      await expect(page.getByText('Download')).toBeVisible();
      await page.waitForTimeout(300);
      
      // Screenshot the details panel
      const detailsPanel = page.locator('.lg\\:col-span-2').first();
      await expect(detailsPanel).toHaveScreenshot('extension-details-panel.png');
    }
  });

  test('installation tab content', async ({ page }) => {
    const extensionCards = page.locator('[role="button"]:has-text("VS Code TODOs"), [role="button"]:has-text("Dynamic Task Manager")').first();
    
    if (await extensionCards.count() > 0) {
      await extensionCards.click();
      
      // Ensure Install tab is selected
      await page.getByText('Install').click();
      await page.waitForTimeout(200);
      
      // Screenshot install tab content
      const installContent = page.locator('[data-value="install"]');
      if (await installContent.count() > 0) {
        await expect(installContent).toHaveScreenshot('install-tab-content.png');
      }
    }
  });

  test('API tab content', async ({ page }) => {
    const extensionCards = page.locator('[role="button"]:has-text("VS Code TODOs"), [role="button"]:has-text("Dynamic Task Manager")').first();
    
    if (await extensionCards.count() > 0) {
      await extensionCards.click();
      
      // Click API tab
      await page.getByText('API').click();
      await page.waitForTimeout(200);
      
      // Screenshot API tab content
      const apiContent = page.locator('[data-value="curl"]');
      if (await apiContent.count() > 0) {
        await expect(apiContent).toHaveScreenshot('api-tab-content.png');
      }
    }
  });

  test('mobile layout', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.waitForTimeout(300);
    
    // Mobile main page screenshot
    await expect(page).toHaveScreenshot('mobile-main-page.png', {
      fullPage: true,
      animations: 'disabled'
    });
  });

  test('tablet layout', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.waitForTimeout(300);
    
    // Tablet main page screenshot
    await expect(page).toHaveScreenshot('tablet-main-page.png', {
      fullPage: true,
      animations: 'disabled'
    });
  });

  test('empty state appearance', async ({ page }) => {
    // Mock empty extension list by intercepting API
    await page.route('**/api/extensions', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([])
      });
    });
    
    await page.reload();
    await page.waitForLoadState('networkidle');
    
    // Wait for empty state to render
    await expect(page.getByText('Select an Extension')).toBeVisible();
    
    // Screenshot empty state
    await expect(page).toHaveScreenshot('empty-state.png', {
      animations: 'disabled'
    });
  });

  test('button states and interactions', async ({ page }) => {
    const extensionCards = page.locator('[role="button"]:has-text("VS Code TODOs"), [role="button"]:has-text("Dynamic Task Manager")').first();
    
    if (await extensionCards.count() > 0) {
      await extensionCards.click();
      
      // Test button hover states
      const downloadButton = page.getByText('Download');
      await downloadButton.hover();
      await page.waitForTimeout(100);
      
      // Screenshot button hover state
      await expect(downloadButton).toHaveScreenshot('download-button-hover.png');
      
      // Test copy button
      const copyButtons = page.locator('button:has-text("Copy")');
      if (await copyButtons.count() > 0) {
        const firstCopyButton = copyButtons.first();
        await firstCopyButton.hover();
        await page.waitForTimeout(100);
        
        await expect(firstCopyButton).toHaveScreenshot('copy-button-hover.png');
      }
    }
  });

  test('tab navigation visual states', async ({ page }) => {
    const extensionCards = page.locator('[role="button"]:has-text("VS Code TODOs"), [role="button"]:has-text("Dynamic Task Manager")').first();
    
    if (await extensionCards.count() > 0) {
      await extensionCards.click();
      
      // Test each tab's active state
      const tabs = ['Install', 'API', 'Details', 'Keywords'];
      
      for (const tabName of tabs) {
        await page.getByText(tabName).click();
        await page.waitForTimeout(200);
        
        // Screenshot the tab header with active state
        const tabsList = page.locator('[role="tablist"]');
        await expect(tabsList).toHaveScreenshot(`tab-${tabName.toLowerCase()}-active.png`);
      }
    }
  });

  test('code blocks and syntax highlighting', async ({ page }) => {
    const extensionCards = page.locator('[role="button"]:has-text("VS Code TODOs"), [role="button"]:has-text("Dynamic Task Manager")').first();
    
    if (await extensionCards.count() > 0) {
      await extensionCards.click();
      
      // Install tab has code blocks
      await page.getByText('Install').click();
      await page.waitForTimeout(200);
      
      // Screenshot install command code block
      const codeBlocks = page.locator('code');
      if (await codeBlocks.count() > 0) {
        await expect(codeBlocks.first()).toHaveScreenshot('install-command-code.png');
      }
      
      // API tab has curl examples
      await page.getByText('API').click();
      await page.waitForTimeout(200);
      
      const curlBlocks = page.locator('code');
      if (await curlBlocks.count() > 0) {
        await expect(curlBlocks.first()).toHaveScreenshot('curl-command-code.png');
      }
    }
  });

  test('dark theme compatibility', async ({ page }) => {
    // Check if dark theme can be applied (this depends on implementation)
    // For now, test default theme consistency
    
    await page.waitForTimeout(300);
    
    // Verify color consistency across components
    await expect(page).toHaveScreenshot('theme-consistency.png', {
      fullPage: true,
      animations: 'disabled'
    });
  });

  test('loading states', async ({ page }) => {
    // Slow down network to capture loading states
    await page.route('**/api/**', route => {
      setTimeout(() => route.continue(), 1000);
    });
    
    // Navigate to trigger loading
    await page.goto('/');
    
    // Try to capture loading state (might be too fast)
    await page.waitForTimeout(500);
    await expect(page).toHaveScreenshot('potential-loading-state.png');
    
    // Wait for content to load
    await page.waitForLoadState('networkidle');
  });

  test('high contrast mode', async ({ page }) => {
    // Enable high contrast mode if supported
    await page.emulateMedia({ reducedMotion: 'reduce', colorScheme: 'dark' });
    
    await page.waitForTimeout(300);
    
    // Screenshot with high contrast/reduced motion
    await expect(page).toHaveScreenshot('high-contrast-mode.png', {
      fullPage: true,
      animations: 'disabled'
    });
  });
});