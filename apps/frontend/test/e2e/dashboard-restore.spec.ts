
import { expect, test } from '@playwright/test';

test('Dashboard Loads', async ({ page }) => {
  await page.goto('/');
  // Basic check for sidebar or header
  await expect(page.getByText('TaskMan v2')).toBeVisible({ timeout: 5000 });
});
