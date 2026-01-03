import { expect, test } from '@playwright/test';

const BASE_URL = 'http://127.0.0.1:5174';

test.describe('Phase 8: Project Intelligence', () => {

    test.beforeEach(async ({ page }) => {
        await page.goto(BASE_URL);
        await expect(page.locator('text=Connected')).toBeVisible({ timeout: 10000 });
    });

    test('Analytics and Bottleneck Radar', async ({ page }) => {
        // 1. Create a Blocked Task
        await page.keyboard.press('c');
        const taskName = `Blocked Task ${Date.now()}`;
        await page.fill('input[placeholder="Task title"]', taskName);

        // Open Priority/Status selector (simplified: assumes default is To Do, we change it via context menu or edit)
        // Actually, let's just create it as To Do, then use Context Menu to Block it?
        // Wait, Context Menu doesn't have "Block" directly, it has "Move to Status" -> "Blocked" (check context menu implementation)
        // I checked TaskContextMenu, it has "Move to Status", let's check values.

        // Alternative: Use Quick Task Form if it supports status (it does, but UI might be tricky).
        // Let's create as To Do, then drag to Blocked column (Kanban) OR update via Context Menu.
        // Assuming Kanban view.
        await page.keyboard.press('Enter');
        await expect(page.locator(`text=${taskName}`)).toBeVisible();

        // 2. Move to Blocked (using Drag and Drop)
        // Locate task and Blocked column
        const taskCard = page.locator(`.group.bg-card:has-text("${taskName}")`).first();
        const blockedColumn = page.locator('h3:has-text("BLOCKED")').locator('..').locator('..'); // Navigate up to droppable area

        await taskCard.dragTo(blockedColumn);

        // 3. Switch to Analytics View
        await page.click('button:has-text("Analytics")');

        // 4. Verify Stat Cards
        await expect(page.locator('text=Velocity Aura')).toBeVisible();
        await expect(page.locator('text=Bottleneck Radar')).toBeVisible();

        // 5. Verify the blocked task is in the Radar
        await expect(page.locator(`text=${taskName}`)).toBeVisible();

        // 6. Verify Blocked Count is > 0
         const valueElement = page.locator('text=Blocked Tasks').locator('..').locator('..').locator('.text-2xl');
         const count = await valueElement.innerText();
         expect(parseInt(count)).toBeGreaterThan(0);
    });
});
