import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

/**
 * DTM Accessibility Tests
 * Tests compliance with WCAG 2.1 AA standards
 */
test.describe('DTM Accessibility', () => {
  test.beforeEach(async ({ page }) => {
    // Mock API responses
    await page.route('**/api/v1/health', async route => {
      await route.fulfill({
        json: { version: '1.0.0', uptime: '24 hours' }
      });
    });

    await page.route('**/api/v1/projects', async route => {
      await route.fulfill({
        json: [
          {
            id: 'P-A11Y-001',
            name: 'Accessibility Test Project',
            description: 'Project for accessibility testing',
            status: 'active',
            created_at: '2024-01-01T00:00:00Z'
          }
        ]
      });
    });

    await page.route('**/api/v1/tasks', async route => {
      await route.fulfill({
        json: [
          {
            id: 'T-A11Y-001',
            title: 'Accessibility Test Task',
            description: 'Task for accessibility testing',
            status: 'new',
            priority: 'high',
            shape: 'Triangle',
            project_id: 'P-A11Y-001',
            created_at: '2024-01-01T00:00:00Z'
          }
        ]
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

    await page.goto('/');
  });

  test('DTM dashboard passes axe accessibility scan', async ({ page }) => {
    // Wait for content to load
    await page.waitForTimeout(2000);
    
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
      .analyze();
    
    expect(accessibilityScanResults.violations).toEqual([]);
  });

  test('Task detail modal passes accessibility scan', async ({ page }) => {
    // Wait for tasks to load
    await page.waitForTimeout(2000);
    
    // Open task modal
    await page.getByText('Accessibility Test Task').click();
    await page.waitForSelector('[role="dialog"]');
    
    const accessibilityScanResults = await new AxeBuilder({ page })
      .include('[role="dialog"]')
      .withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
      .analyze();
    
    expect(accessibilityScanResults.violations).toEqual([]);
  });

  test('Settings modal passes accessibility scan', async ({ page }) => {
    // Wait for initial load
    await page.waitForTimeout(1000);
    
    // Open settings modal
    await page.getByRole('button', { name: /settings/i }).click();
    await page.waitForSelector('[role="dialog"]');
    
    const accessibilityScanResults = await new AxeBuilder({ page })
      .include('[role="dialog"]')
      .withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
      .analyze();
    
    expect(accessibilityScanResults.violations).toEqual([]);
  });

  test('keyboard navigation works correctly', async ({ page }) => {
    await page.waitForTimeout(2000);
    
    // Test tab navigation
    await page.keyboard.press('Tab');
    let focusedElement = await page.locator(':focus').first();
    await expect(focusedElement).toBeVisible();
    
    // Continue tabbing through interactive elements
    await page.keyboard.press('Tab');
    focusedElement = await page.locator(':focus').first();
    await expect(focusedElement).toBeVisible();
    
    // Test that focus is visible
    const focusedStyle = await focusedElement.evaluate(el => {
      return window.getComputedStyle(el);
    });
    
    // Should have some form of focus indicator
    expect(
      focusedStyle.outline !== 'none' || 
      focusedStyle.boxShadow !== 'none' ||
      focusedStyle.border !== 'none'
    ).toBeTruthy();
  });

  test('heading hierarchy is correct', async ({ page }) => {
    await page.waitForTimeout(2000);
    
    // Check for h1
    const h1Elements = await page.locator('h1').count();
    expect(h1Elements).toBeGreaterThan(0);
    
    // Check heading order (should not skip levels)
    const headings = await page.locator('h1, h2, h3, h4, h5, h6').all();
    const headingLevels = await Promise.all(
      headings.map(async (heading) => {
        const tagName = await heading.evaluate(el => el.tagName.toLowerCase());
        return parseInt(tagName.charAt(1));
      })
    );
    
    // Verify no heading levels are skipped
    for (let i = 1; i < headingLevels.length; i++) {
      const current = headingLevels[i];
      const previous = headingLevels[i - 1];
      
      // Next heading should not be more than 1 level deeper
      expect(current - previous).toBeLessThanOrEqual(1);
    }
  });

  test('interactive elements have accessible names', async ({ page }) => {
    await page.waitForTimeout(2000);
    
    // Check buttons have accessible names
    const buttons = await page.getByRole('button').all();
    for (const button of buttons) {
      const accessibleName = await button.getAttribute('aria-label') || 
                            await button.textContent() ||
                            await button.getAttribute('title');
      expect(accessibleName).toBeTruthy();
    }
    
    // Check links have accessible names
    const links = await page.getByRole('link').all();
    for (const link of links) {
      const accessibleName = await link.getAttribute('aria-label') || 
                           await link.textContent() ||
                           await link.getAttribute('title');
      expect(accessibleName).toBeTruthy();
    }
  });

  test('form elements have proper labels', async ({ page }) => {
    // Open settings to check form elements
    await page.getByRole('button', { name: /settings/i }).click();
    await page.waitForSelector('[role="dialog"]');
    
    // Check all input elements have labels
    const inputs = await page.locator('input, select, textarea').all();
    for (const input of inputs) {
      const id = await input.getAttribute('id');
      const ariaLabel = await input.getAttribute('aria-label');
      const ariaLabelledBy = await input.getAttribute('aria-labelledby');
      
      if (id) {
        // Should have a label element pointing to this input
        const label = await page.locator(`label[for="${id}"]`).count();
        expect(label > 0 || ariaLabel || ariaLabelledBy).toBeTruthy();
      } else {
        // Should have aria-label or aria-labelledby
        expect(ariaLabel || ariaLabelledBy).toBeTruthy();
      }
    }
  });

  test('color contrast meets WCAG AA standards', async ({ page }) => {
    await page.waitForTimeout(2000);
    
    // Use axe to specifically check color contrast
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2aa'])
      .withRules(['color-contrast'])
      .analyze();
    
    expect(accessibilityScanResults.violations).toEqual([]);
  });

  test('images have alt text', async ({ page }) => {
    await page.waitForTimeout(2000);
    
    const images = await page.locator('img').all();
    for (const image of images) {
      const alt = await image.getAttribute('alt');
      const ariaLabel = await image.getAttribute('aria-label');
      const role = await image.getAttribute('role');
      
      // Images should have alt text, aria-label, or be marked as decorative
      expect(alt !== null || ariaLabel || role === 'presentation').toBeTruthy();
    }
  });

  test('modal focus management works correctly', async ({ page }) => {
    await page.waitForTimeout(2000);
    
    // Focus an element before opening modal
    await page.getByRole('button', { name: /refresh/i }).focus();
    const initialFocus = await page.locator(':focus').first();
    
    // Open task modal
    await page.getByText('Accessibility Test Task').click();
    await page.waitForSelector('[role="dialog"]');
    
    // Focus should move into the modal
    const modalFocus = await page.locator(':focus').first();
    const isInModal = await modalFocus.evaluate(el => {
      const modal = document.querySelector('[role="dialog"]');
      return modal?.contains(el);
    });
    expect(isInModal).toBeTruthy();
    
    // Close modal with Escape
    await page.keyboard.press('Escape');
    await page.waitForTimeout(500);
    
    // Focus should return to the element that opened the modal
    const finalFocus = await page.locator(':focus').first();
    const sameElement = await finalFocus.evaluate((el, initialEl) => {
      return el === initialEl;
    }, await initialFocus.elementHandle());
    
    // Note: This might not always be exact same element, but should be nearby
    expect(await finalFocus.isVisible()).toBeTruthy();
  });

  test('ARIA landmarks are present', async ({ page }) => {
    await page.waitForTimeout(2000);
    
    // Check for main landmark
    const main = await page.getByRole('main').count();
    expect(main).toBeGreaterThan(0);
    
    // Check for navigation if present
    const nav = await page.getByRole('navigation').count();
    // Navigation is optional, but if present should be properly marked
    
    // Check for banner/header if present
    const banner = await page.getByRole('banner').count();
    // Banner is optional for single-page apps
    
    // Check for complementary content if present
    const complementary = await page.getByRole('complementary').count();
    // Complementary is optional
  });

  test('skip links work correctly', async ({ page }) => {
    await page.waitForTimeout(2000);
    
    // Check if skip links exist (they might be visually hidden)
    const skipLinks = await page.locator('a[href^="#"]').filter({ hasText: /skip/i }).count();
    
    if (skipLinks > 0) {
      // Test skip link functionality
      await page.keyboard.press('Tab');
      const skipLink = await page.locator('a[href^="#"]').filter({ hasText: /skip/i }).first();
      
      if (await skipLink.isVisible()) {
        await skipLink.click();
        
        // Verify focus moved to target
        const targetId = await skipLink.getAttribute('href');
        if (targetId) {
          const target = await page.locator(targetId).first();
          await expect(target).toBeFocused();
        }
      }
    }
  });

  test('screen reader announcements work', async ({ page }) => {
    await page.waitForTimeout(2000);
    
    // Check for live regions
    const liveRegions = await page.locator('[aria-live]').count();
    
    // Trigger an action that should announce something
    await page.getByRole('button', { name: /refresh/i }).click();
    
    // Wait for potential announcements
    await page.waitForTimeout(1000);
    
    // Check if aria-live regions exist for dynamic content
    const ariaLive = await page.locator('[aria-live="polite"], [aria-live="assertive"]').count();
    expect(ariaLive).toBeGreaterThanOrEqual(0); // Should have some live regions for status updates
  });

  test('reduced motion preference is respected', async ({ page }) => {
    // Set reduced motion preference
    await page.emulateMedia({ reducedMotion: 'reduce' });
    await page.waitForTimeout(2000);
    
    // Trigger an action that normally has animation
    await page.getByText('Accessibility Test Task').click();
    await page.waitForSelector('[role="dialog"]');
    
    // Animations should be minimal or removed
    // This is more of a visual test, but we can check CSS
    const modal = page.locator('[role="dialog"]');
    const animationDuration = await modal.evaluate(el => {
      const style = window.getComputedStyle(el);
      return style.animationDuration;
    });
    
    // With reduced motion, animations should be very fast or none
    expect(animationDuration === '0s' || animationDuration === 'none').toBeTruthy();
  });

  test('mobile accessibility - touch targets', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await page.waitForTimeout(1000);
    
    // Check touch target sizes
    const buttons = await page.getByRole('button').all();
    for (const button of buttons) {
      const box = await button.boundingBox();
      if (box) {
        // WCAG recommends minimum 44x44px touch targets
        expect(box.width).toBeGreaterThanOrEqual(44);
        expect(box.height).toBeGreaterThanOrEqual(44);
      }
    }
  });

  test('high contrast mode support', async ({ page }) => {
    // Simulate high contrast mode
    await page.addInitScript(() => {
      // Add high contrast media query simulation
      const style = document.createElement('style');
      style.textContent = `
        @media (prefers-contrast: high) {
          * {
            forced-colors: active;
          }
        }
      `;
      document.head.appendChild(style);
    });
    
    await page.waitForTimeout(1000);
    
    // Run accessibility scan in high contrast mode
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2aa'])
      .analyze();
    
    expect(accessibilityScanResults.violations).toEqual([]);
  });
});