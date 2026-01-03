
import { expect, test } from '@playwright/test';

test('Data Explorer Test', async ({ page }) => {
  await page.goto('/');

  // wait for dashboard
  await expect(page.getByText('TaskMan v3')).toBeVisible();

  // Navigate to Data Explorer
  await page.getByText('Explorer').click();

  // Verify Title
  await expect(page.getByText('Data Explorer')).toBeVisible();

  // Verify Tabs
  await expect(page.getByRole('tab', { name: /Tasks/ })).toBeVisible();
  await expect(page.getByRole('tab', { name: /Projects/ })).toBeVisible();
  await expect(page.getByRole('tab', { name: /Sprints/ })).toBeVisible();
  await expect(page.getByRole('tab', { name: /Action Lists/ })).toBeVisible();

  // Verify Table Content (assuming some data exists or at least empty table headers)
  await expect(page.getByRole('columnheader', { name: 'title' })).toBeVisible();
  await expect(page.getByRole('columnheader', { name: 'status' })).toBeVisible();

  // Test JSON toggle
  await page.getByRole('button', { name: 'View JSON' }).click();
  await expect(page.locator('pre')).toBeVisible(); // JSON view
  await page.getByRole('button', { name: 'View Table' }).click();
  await expect(page.locator('table')).toBeVisible(); // Table view
});
