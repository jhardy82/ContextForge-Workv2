import { expect, test } from "@playwright/test";

test.use({ baseURL: "http://localhost:5002" });

test.describe("AI Input Validation", () => {
  test("should parse and create task from natural language", async ({ page }) => {
    await page.goto("/");

    // 1. Locate the AI input
    const aiInput = page.getByPlaceholder("Ask AI to create a task...");
    await expect(aiInput).toBeVisible();

    // 2. Type a command with metadata
    const taskTitle = `Critical Bug Fix ${Date.now()}`;
    await aiInput.fill(`${taskTitle} priority:high #bug`);

    // 3. Verify Preview Chips appear
    // We expect "Priority: high" and "#bug" chips
    await expect(page.getByText("Priority: high")).toBeVisible();
    await expect(page.getByText("#bug")).toBeVisible();

    // 4. Submit
    await page.keyboard.press("Enter");

    // 5. Verify Toast
    await expect(page.getByText("Task created")).toBeVisible();

    // 6. Verify Task on Board
    // Should be in "To Do" (default) and have high priority indicator (usually represented by color/icon)
    // We'll just check it exists for now
    await expect(page.getByText(taskTitle)).toBeVisible();
  });
});
