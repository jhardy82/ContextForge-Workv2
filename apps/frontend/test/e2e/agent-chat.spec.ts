import { expect, test } from '@playwright/test';

const BASE_URL = 'http://127.0.0.1:5174';

test.describe('Phase 8: Agent Chat Sidebar', () => {

    test.beforeEach(async ({ page }) => {
        await page.goto(BASE_URL);
        await expect(page.locator('text=Connected')).toBeVisible({ timeout: 10000 });
    });

    test('Open Chat and Send Message', async ({ page }) => {
        // 1. Verify Agent Button exists
        const agentBtn = page.locator('button:has-text("Agent")');
        await expect(agentBtn).toBeVisible();

        // 2. Open Sidebar
        await agentBtn.click();
        await expect(page.locator('h3:has-text("Agent Chat")')).toBeVisible();

        // 3. Send a Message
        const message = "Show me high priority tasks";
        await page.fill('textarea[placeholder*="Ask the agent"]', message);
        await page.click('button:has(.lucide-send)');

        // 4. Verify Message Appears
        await expect(page.locator(`p:has-text("${message}")`)).toBeVisible();

        // 5. Verify Response (Simulated)
        // Wait for typing... and then response
        await expect(page.locator('text=I received your command')).toBeVisible({ timeout: 5000 });

        // 6. Close Sidebar
        await page.click('button:has(.lucide-x)'); // Close button
        await expect(page.locator('h3:has-text("Agent Chat")')).not.toBeVisible();
    });
});
