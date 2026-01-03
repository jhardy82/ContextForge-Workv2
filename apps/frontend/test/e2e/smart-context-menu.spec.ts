import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

const BASE_URL = "http://127.0.0.1:5174";

test.describe("Phase 8: Smart Context Menu", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(BASE_URL);
    await expect(page.locator("text=Connected")).toBeVisible({
      timeout: 10000,
    });

    // Ensure at least one task exists
    await page.keyboard.press("c"); // Quick create shortcut
    await page.fill(
      'input[placeholder="Task title"]',
      `Context Menu Test ${Date.now()}`
    );
    await page.keyboard.press("Enter");
    await expect(page.locator("text=Task created")).toBeVisible();
  });

  test("Context Menu Actions", async ({ page }) => {
    // 1. Locate a task card
    const taskCard = page.locator(".group.bg-card").first();
    await expect(taskCard).toBeVisible();

    // 2. Right-click to open Context Menu
    await taskCard.click({ button: "right" });
    await expect(page.locator("text=AI CONSTALLATION")).toBeVisible();

    // [Layer: Accessibility] Scan the Menu for issues
    const results = await new AxeBuilder({ page })
      .include(".radix-context-menu-content") // Target the menu
      .analyze();

    expect(results.violations).toEqual([]); // Assert no violations

    // 3. Test AI Action (Breakdown)
    await page.click("text=Auto-Breakdown Task");
    await expect(page.locator("text=AI Agent is thinking...")).toBeVisible();

    // Wait for success toast (simulated 2s delay)
    await expect(page.locator("text=Task decomposed")).toBeVisible({
      timeout: 5000,
    });

    // 4. Test Duplicate
    await taskCard.click({ button: "right" });
    await page.click("text=Duplicate");
    await expect(page.locator("text=Task created")).toBeVisible();
    await expect(page.locator("text=(Copy)")).toBeVisible();

    // 5. Test Delete
    // Right click the copy
    const copyCard = page.locator('div:has-text("(Copy)")').last();
    await copyCard.click({ button: "right" });

    // Click delete
    await page.click("text=Delete Task");
    await expect(page.locator("text=Task deleted")).toBeVisible();

    // Verify copy is gone (wait a bit for refetch)
    await page.waitForTimeout(1000);
    await expect(
      page.locator('div:has-text("(Copy)")').last()
    ).not.toBeVisible();
  });
});
