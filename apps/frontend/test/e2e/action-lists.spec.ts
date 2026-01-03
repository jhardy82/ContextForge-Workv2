import { expect, test } from '@playwright/test';

const BASE_URL = 'http://127.0.0.1:5174';

test.describe('Phase 8: Action List UI', () => {

    test.beforeEach(async ({ page }) => {
        await page.goto(BASE_URL);
        await expect(page.locator('text=Connected')).toBeVisible({ timeout: 10000 });
    });

    test('Create and Manage Action Lists', async ({ page }) => {
        // 1. Navigate to Action Lists View
        await page.click('button:has-text("Action Lists")');
        await expect(page.locator('h2:has-text("Action Lists")')).toBeVisible();

        // 2. Create a new List
        const listName = `Emergency Deployment ${Date.now()}`;
        await page.fill('input[placeholder="Create a new action list..."]', listName);
        await page.click('button:has(.lucide-plus)'); // Submit button

        // 3. Verify List Exists
        await expect(page.locator(`text=${listName}`)).toBeVisible();

        // 4. Add an Item to the List
        const listCard = page.locator(`.glass-card:has-text("${listName}")`);
        const itemText = "Check server logs";
        await listCard.locator('input[placeholder="Add item..."]').fill(itemText);
        await listCard.locator('button:has(.lucide-plus)').nth(1).click(); // Add item button

        // 5. Verify Item Exists
        await expect(listCard.locator(`text=${itemText}`)).toBeVisible();

        // 6. Toggle Item Item
        await listCard.locator('button:has(.lucide-circle)').click();
    });
});
