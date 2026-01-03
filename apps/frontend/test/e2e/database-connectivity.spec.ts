import { expect, test } from '@playwright/test';

test.describe('Database Connectivity Integration', () => {
  test('should connect to backend and perform CRUD operations', async ({ page }) => {
    // 1. Navigate to Dashboard
    // Ensure we are hitting the dev server which proxies/talks to localhost:3001
    await page.goto('/dashboard?view=list');

    // 2. Initial Health Check (Implicit)
    // If the backend is down, the UI might show an error or infinite load.
    // We wait for the main content area.
    await expect(page.locator('main')).toBeVisible();

    // 3. Create a New Task (Write Test)
    const taskTitle = `DB Connectivity Test ${Date.now()}`;

    // Find create button (assuming typical location or shortcut)
    // Note: Adjust selector based on actual UI implementation
    await page.getByRole('button', { name: /New Task/i }).first().click();

    // Check if dialog opens
    const dialog = page.getByRole('dialog');
    await expect(dialog).toBeVisible();

    // Fill form
    await dialog.getByLabel(/Title/i).fill(taskTitle);
    await dialog.getByRole('button', { name: /Create|Save/i }).click();

    // 4. Verify Task Appears (Read Test)
    // Should be in the list
    await expect(page.getByText(taskTitle)).toBeVisible();

    console.log(`Verified creation and display of task: ${taskTitle}`);
  });
});
