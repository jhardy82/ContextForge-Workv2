import { expect, test } from "@playwright/test";

test.describe("Greenfield Edit Mode (Mock Backend)", () => {
  test.beforeEach(async ({ page }) => {
    // Clear localStorage before each test to ensure clean state
    await page.goto("/greenfield.html");

    // Capture logging
    page.on("console", (msg) => console.log(`PAGE LOG: ${msg.text()}`));
    page.on("pageerror", (exception) =>
      console.log(`PAGE ERROR: ${exception}`)
    );

    await page.evaluate(() => localStorage.clear());
    await page.reload();
  });

  test("should seed data, edit task title, and persist changes", async ({
    page,
  }) => {
    console.log("Starting test...");
    // 1. Initial State: Verify Empty
    await expect(page.getByText("PROJECT EXPLORER")).toBeVisible();

    // 2. Smart Seed
    const seedButton = page.getByTitle("Smart Seed");
    await seedButton.click();
    console.log("Clicked Smart Seed");
    await page.waitForLoadState("networkidle");

    // 3. Verify Seed Success (Implicitly by waiting for task)
    // We skip ensuring specific toasts because they might vary if project already exists
    // The ultimate proof is the task appearing in the tree.
    console.log("Waiting for task node...");

    // 4. Verify Tree Population
    // Find the tree node row explicitly to ensure click hits the container with the handler
    const taskNode = page
      .locator('[data-testid^="tree-node-"]')
      .filter({ hasText: "Implement Authentication" })
      .first();
    await expect(taskNode).toBeVisible({ timeout: 10000 });
    console.log("Task node visible");

    // 5. Select Task
    await taskNode.click();
    console.log("Clicked task node");

    // 6. Verify Detail Panel (View Mode)
    await expect(
      page.getByRole("heading", {
        name: "Implement Authentication",
        exact: false,
      })
    ).toBeVisible();
    console.log("Detail panel heading visible");

    // 7. Enter Edit Mode
    // Use robust test IDs
    const editButton = page.getByTestId("edit-task-button");
    await editButton.click();
    console.log("Clicked Edit button");

    // 8. Edit Task Title
    // Find input by value is still best for dynamic content or just find the only text input since it's the title
    // But value matching is fine
    const titleInput = page.locator('input[value*="Implement Authentication"]');
    await expect(titleInput).toBeVisible();
    console.log("Title input visible");

    const newTitle = "Auth Verified Automated";
    await titleInput.fill(newTitle);
    console.log("Filled new title");

    // 9. Keep Save Flow
    // Use robust test IDs
    const saveButton = page.getByTestId("save-task-button");
    await saveButton.click();
    console.log("Clicked Save button");

    // Verify Toast
    await expect(page.locator("text=Task Updated").first()).toBeVisible();
    console.log("Task Updated toast visible");

    // 10. Verify Persistence (Reload)
    await page.reload();
    console.log("Reloaded page");

    // Check Tree Again
    const updatedTaskNode = page
      .locator('[data-testid^="tree-node-"]')
      .filter({ hasText: newTitle })
      .first();
    await expect(updatedTaskNode).toBeVisible();
    console.log("Updated task node visible in tree");

    // Select it again to check detail panel
    await updatedTaskNode.click();
    // Verify updated title in View Mode
    await expect(page.getByRole("heading", { name: newTitle })).toBeVisible();
    console.log("Updated heading visible in detail panel");

    // Sentinel for verification
    const fs = require("fs");
    fs.writeFileSync(
      "e2e-success.txt",
      "Test Passed at " + new Date().toISOString()
    );
    console.log("Sentinel written");
  });
});
