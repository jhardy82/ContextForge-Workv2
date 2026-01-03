import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

/**
 * Comprehensive Accessibility Testing Suite
 * Tests WCAG 2.1 AA compliance, keyboard navigation, screen reader support,
 * and modern accessibility best practices
 */
test.describe('Comprehensive Accessibility Tests', () => {
  
  test.beforeEach(async ({ page }) => {
    // Setup mock API responses for consistent testing
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
            name: 'Accessibility Test Project',
            description: 'Testing accessibility features',
            status: 'active',
            created: new Date().toISOString(),
            updated: new Date().toISOString()
          }
        ]
      });
    });

    await page.route('**/api/v1/tasks', async route => {
      await route.fulfill({
        json: [
          {
            id: '1',
            title: 'High Priority Accessibility Task',
            description: 'Ensure WCAG compliance across all components',
            status: 'new',
            priority: 'high',
            projectId: '1',
            created: new Date().toISOString(),
            updated: new Date().toISOString(),
            assignee: 'accessibility-tester',
            tags: ['accessibility', 'wcag', 'priority']
          },
          {
            id: '2', 
            title: 'Screen Reader Support Task',
            description: 'Implement proper ARIA labels and semantic markup',
            status: 'in-progress',
            priority: 'medium',
            projectId: '1',
            created: new Date().toISOString(),
            updated: new Date().toISOString(),
            assignee: 'a11y-developer',
            tags: ['screen-reader', 'aria']
          }
        ]
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

    await page.goto('/');
  });

  test('meets WCAG 2.1 AA standards on main page', async ({ page }) => {
    await page.waitForTimeout(2000); // Allow content to load
    
    // Run comprehensive accessibility check using AxeBuilder
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
      .analyze();

    // Check for violations
    expect(accessibilityScanResults.violations).toEqual([]);
  });

  test('has proper heading hierarchy', async ({ page }) => {
    await page.waitForTimeout(1000);
    
    // Check for proper heading structure
    const h1 = await page.locator('h1').count();
    expect(h1).toBe(1); // Should have exactly one h1
    
    // Check that main heading is visible and meaningful
    const mainHeading = page.getByRole('heading', { level: 1 });
    await expect(mainHeading).toBeVisible();
    await expect(mainHeading).toContainText(/dtm task manager/i);
    
    // Check heading hierarchy (no skipped levels)
    const headings = await page.locator('h1, h2, h3, h4, h5, h6').all();
    let previousLevel = 0;
    
    for (const heading of headings) {
      const tagName = await heading.evaluate(el => el.tagName);
      const currentLevel = parseInt(tagName.charAt(1));
      
      if (previousLevel > 0) {
        expect(currentLevel).toBeLessThanOrEqual(previousLevel + 1);
      }
      
      previousLevel = currentLevel;
    }
  });

  test('supports comprehensive keyboard navigation', async ({ page }) => {
    await page.waitForTimeout(2000);
    
    // Start with first focusable element
    await page.keyboard.press('Tab');
    
    // Track focus path
    const focusedElements: Array<{tagName: string, role: string | null, ariaLabel: string | null, text: string | null}> = [];
    let previousFocus: any = null;
    
    // Navigate through all interactive elements
    for (let i = 0; i < 20; i++) {
      const focused = await page.locator(':focus').first();
      
      if (await focused.isVisible()) {
        const tagName = await focused.evaluate(el => el.tagName);
        const role = await focused.getAttribute('role');
        const ariaLabel = await focused.getAttribute('aria-label');
        
        focusedElements.push({
          tagName,
          role,
          ariaLabel,
          text: await focused.textContent()
        });
        
        // Ensure focus is visible (focus indicator)
        const focusStyles = await focused.evaluate(el => {
          const styles = window.getComputedStyle(el, ':focus');
          return {
            outline: styles.outline,
            outlineWidth: styles.outlineWidth,
            outlineStyle: styles.outlineStyle,
            boxShadow: styles.boxShadow
          };
        });
        
        // Should have visible focus indicator
        const hasFocusIndicator = 
          focusStyles.outline !== 'none' || 
          focusStyles.outlineWidth !== '0px' ||
          focusStyles.boxShadow !== 'none';
          
        expect(hasFocusIndicator).toBe(true);
        
        if (previousFocus && await previousFocus.isVisible()) {
          expect(focused).not.toBe(previousFocus);
        }
        
        previousFocus = focused;
      }
      
      await page.keyboard.press('Tab');
    }
    
    // Should have focused multiple interactive elements
    expect(focusedElements.length).toBeGreaterThan(3);
    
    // Test reverse tab navigation
    await page.keyboard.press('Shift+Tab');
    const reverseFocused = await page.locator(':focus').first();
    await expect(reverseFocused).toBeVisible();
  });

  test('provides proper ARIA labels and descriptions', async ({ page }) => {
    await page.waitForTimeout(2000);
    
    // Check buttons have proper labels
    const buttons = await page.locator('button').all();
    
    for (const button of buttons) {
      if (await button.isVisible()) {
        const accessibleName = await button.evaluate(el => {
          return el.getAttribute('aria-label') || 
                 el.getAttribute('aria-labelledby') ||
                 el.textContent?.trim() ||
                 el.getAttribute('title');
        });
        
        expect(accessibleName).toBeTruthy();
        expect(accessibleName?.length).toBeGreaterThan(0);
      }
    }
    
    // Check form inputs have labels
    const inputs = await page.locator('input, select, textarea').all();
    
    for (const input of inputs) {
      if (await input.isVisible()) {
        const hasLabel = await input.evaluate(el => {
          const id = el.id;
          const ariaLabel = el.getAttribute('aria-label');
          const ariaLabelledby = el.getAttribute('aria-labelledby');
          const labelElement = id ? document.querySelector(`label[for="${id}"]`) : null;
          const parentLabel = el.closest('label');
          
          return !!(ariaLabel || ariaLabelledby || labelElement || parentLabel);
        });
        
        expect(hasLabel).toBe(true);
      }
    }
    
    // Check images have alt text
    const images = await page.locator('img').all();
    
    for (const img of images) {
      if (await img.isVisible()) {
        const altText = await img.getAttribute('alt');
        const ariaLabel = await img.getAttribute('aria-label');
        const role = await img.getAttribute('role');
        
        // Decorative images should have empty alt or role="presentation"
        // Content images should have meaningful alt text
        expect(
          altText !== null || 
          ariaLabel || 
          role === 'presentation' || 
          role === 'img'
        ).toBe(true);
      }
    }
  });

  test('handles dynamic content accessibility', async ({ page }) => {
    await page.waitForTimeout(2000);
    
    // Test modal accessibility
    const taskElement = page.getByText('High Priority Accessibility Task').first();
    if (await taskElement.isVisible()) {
      await taskElement.click();
      
      // Modal should have proper ARIA attributes
      const modal = page.getByRole('dialog');
      await expect(modal).toBeVisible();
      await expect(modal).toHaveAttribute('aria-modal', 'true');
      
      // Check if modal has accessible name
      const modalName = await modal.evaluate(el => {
        return el.getAttribute('aria-labelledby') || 
               el.getAttribute('aria-label') ||
               el.querySelector('h1, h2, h3, h4, h5, h6')?.textContent;
      });
      expect(modalName).toBeTruthy();
      
      // Focus should be trapped in modal
      const focusableInModal = await modal.locator('button, input, select, textarea, a[href], [tabindex]:not([tabindex="-1"])').count();
      expect(focusableInModal).toBeGreaterThan(0);
      
      // First focusable element should be focused
      const firstFocusable = modal.locator('button, input, select, textarea, a[href], [tabindex]:not([tabindex="-1"])').first();
      if (await firstFocusable.isVisible()) {
        await expect(firstFocusable).toBeFocused();
      }
      
      // Close modal with Escape
      await page.keyboard.press('Escape');
      await expect(modal).not.toBeVisible();
    }
  });

  test('provides accessible status indicators', async ({ page }) => {
    await page.waitForTimeout(2000);
    
    // Check connection status accessibility
    const connectionStatus = page.locator('[data-testid="connection-status"]');
    if (await connectionStatus.isVisible()) {
      const ariaLabel = await connectionStatus.getAttribute('aria-label');
      const role = await connectionStatus.getAttribute('role');
      const textContent = await connectionStatus.textContent();
      
      // Should have meaningful status indication
      expect(
        ariaLabel?.includes('connect') || 
        textContent?.includes('connect') ||
        role === 'status'
      ).toBe(true);
    }
    
    // Check task status badges
    const statusBadges = await page.locator('[data-status], .status-badge, .badge').all();
    
    for (const badge of statusBadges) {
      if (await badge.isVisible()) {
        const statusText = await badge.textContent();
        const ariaLabel = await badge.getAttribute('aria-label');
        
        // Status should be communicated to screen readers
        expect(statusText || ariaLabel).toBeTruthy();
        
        // Should not rely only on color for status indication
        const hasTextualIndicator = statusText && statusText.trim().length > 0;
        expect(hasTextualIndicator).toBe(true);
      }
    }
  });

  test('meets color contrast requirements', async ({ page }) => {
    await page.waitForTimeout(2000);
    
    // Run axe color contrast checks
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withRules(['color-contrast', 'color-contrast-enhanced'])
      .analyze();
    
    expect(accessibilityScanResults.violations).toEqual([]);
    
    // Additional manual contrast checks for key elements
    const textElements = await page.locator('h1, h2, h3, h4, h5, h6, p, span, button, a').all();
    
    for (const element of textElements.slice(0, 10)) { // Sample first 10 elements
      if (await element.isVisible()) {
        const styles = await element.evaluate(el => {
          const computed = window.getComputedStyle(el);
          return {
            color: computed.color,
            backgroundColor: computed.backgroundColor,
            fontSize: computed.fontSize
          };
        });
        
        // Elements should have defined colors (not just transparent)
        expect(styles.color).not.toBe('rgba(0, 0, 0, 0)');
        expect(styles.color).not.toBe('transparent');
      }
    }
  });

  test('supports screen reader announcements', async ({ page }) => {
    await page.waitForTimeout(2000);
    
    // Check for live regions
    const liveRegions = await page.locator('[aria-live], [role="status"], [role="alert"]').all();
    
    // Should have at least one live region for dynamic updates
    expect(liveRegions.length).toBeGreaterThan(0);
    
    // Test refresh functionality announcements
    const refreshButton = page.getByRole('button', { name: /refresh/i });
    if (await refreshButton.isVisible()) {
      await refreshButton.click();
      
      // Should provide feedback about the action
      const feedback = page.locator('[aria-live="polite"], [aria-live="assertive"], [role="status"]');
      
      // Wait for potential announcements
      await page.waitForTimeout(1000);
      
      // At least one feedback mechanism should exist
      expect(await feedback.count()).toBeGreaterThan(0);
    }
  });

  test('handles error states accessibly', async ({ page }) => {
    // Mock error responses
    await page.route('**/api/v1/health', async route => {
      await route.fulfill({
        status: 500,
        json: { error: 'Connection failed' }
      });
    });
    
    await page.route('**/api/v1/tasks', async route => {
      await route.fulfill({
        status: 404,
        json: { error: 'Tasks not found' }
      });
    });
    
    await page.reload();
    await page.waitForTimeout(3000);
    
    // Error messages should be accessible
    const errorElements = await page.locator('[role="alert"], .error, [aria-live="assertive"]').all();
    
    for (const error of errorElements) {
      if (await error.isVisible()) {
        const text = await error.textContent();
        const ariaLabel = await error.getAttribute('aria-label');
        
        // Error should have meaningful text
        expect(text || ariaLabel).toBeTruthy();
        
        // Should be announced to screen readers
        const role = await error.getAttribute('role');
        const ariaLive = await error.getAttribute('aria-live');
        
        expect(
          role === 'alert' || 
          ariaLive === 'assertive' || 
          ariaLive === 'polite'
        ).toBe(true);
      }
    }
  });

  test('mobile accessibility features work correctly', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await page.waitForTimeout(2000);
    
    // Check touch targets are large enough (minimum 44px)
    const interactiveElements = await page.locator('button, a, input, select, textarea, [role="button"], [tabindex="0"]').all();
    
    for (const element of interactiveElements) {
      if (await element.isVisible()) {
        const box = await element.boundingBox();
        
        if (box) {
          // WCAG AA requires minimum 44px touch targets
          expect(Math.max(box.width, box.height)).toBeGreaterThanOrEqual(44);
        }
      }
    }
    
    // Test mobile-specific accessibility features
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
      .analyze();
    
    expect(accessibilityScanResults.violations).toEqual([]);
  });

  test('supports high contrast mode', async ({ page }) => {
    // Simulate high contrast mode
    await page.addInitScript(() => {
      // Override matchMedia to simulate high contrast preference
      (window as any).matchMedia = (query: string) => ({
        matches: query === '(prefers-contrast: high)',
        media: query,
        onchange: null,
        addListener: () => {},
        removeListener: () => {},
        addEventListener: () => {},
        removeEventListener: () => {},
        dispatchEvent: () => {},
      });
    });
    
    await page.goto('/');
    await page.waitForTimeout(2000);
    
    // Elements should still be visible and functional in high contrast
    await expect(page.getByRole('heading', { name: /dtm task manager/i })).toBeVisible();
    
    // Interactive elements should maintain functionality
    const refreshButton = page.getByRole('button', { name: /refresh/i });
    if (await refreshButton.isVisible()) {
      await expect(refreshButton).toBeEnabled();
    }
    
    // Run accessibility check in high contrast mode
    const accessibilityScanResults = await new AxeBuilder({ page }).analyze();
    expect(accessibilityScanResults.violations).toEqual([]);
  });

  test('provides alternative interaction methods', async ({ page }) => {
    await page.waitForTimeout(2000);
    
    // Test that all functionality is available via keyboard
    const buttons = await page.locator('button').all();
    
    for (const button of buttons) {
      if (await button.isVisible()) {
        // Focus the button
        await button.focus();
        await expect(button).toBeFocused();
        
        // Should be activatable with Enter
        const isDisabled = await button.isDisabled();
        if (!isDisabled) {
          // Test Enter key activation
          await page.keyboard.press('Enter');
          // Note: We don't test the action result here, just that it's keyboard accessible
        }
        
        // Should be activatable with Space for buttons
        await button.focus();
        if (!isDisabled) {
          await page.keyboard.press('Space');
        }
      }
    }
    
    // Test that links are keyboard accessible
    const links = await page.locator('a[href]').all();
    
    for (const link of links) {
      if (await link.isVisible()) {
        await link.focus();
        await expect(link).toBeFocused();
        
        // Should be activatable with Enter
        await page.keyboard.press('Enter');
        // Note: We're not following the link, just testing keyboard activation
      }
    }
  });
});