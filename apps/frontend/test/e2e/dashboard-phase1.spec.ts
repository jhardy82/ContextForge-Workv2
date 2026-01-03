import { expect, test } from "@playwright/test";

test.use({ baseURL: "http://localhost:5002" });

test.describe("Dashboard V3 Phase 1 Validation", () => {
  test("should render the dashboard layout correctly", async ({ page }) => {
    // 1. Navigate to dashboard
    await page.goto("/");

    // 2. Verify Header
    await expect(
      page.getByRole("heading", { name: "TaskMan v3" })
    ).toBeVisible();
    await expect(page.getByText("Connected")).toBeVisible();

    // 3. Verify Stats Cards
    await expect(page.getByText("Total Tasks")).toBeVisible();
    await expect(page.getByText("In Progress")).toBeVisible();
    await expect(page.getByText("Completed")).toBeVisible();
    await expect(page.getByText("Blocked")).toBeVisible();

    // 4. Verify Kanban Board Columns
    const columns = [
      "To Do",
      "In Progress",
      "In Review",
      "Completed",
      "Blocked",
    ];
    for (const column of columns) {
      await expect(page.getByText(column, { exact: true })).toBeVisible();
    }
  });

  test("should open command palette with keyboard shortcut", async ({
    page,
  }) => {
    await page.goto("/");

    // Press Cmd+K (or Ctrl+K)
    if (process.platform === "darwin") {
      await page.keyboard.press("Meta+K");
    } else {
      await page.keyboard.press("Control+K");
    }

    // Verify dialog appears
    await expect(
      page.getByPlaceholder("Type a command or search...")
    ).toBeVisible();

    // Verify actions exist
    await expect(page.getByText("Create new task")).toBeVisible();
    await expect(page.getByText("Switch to Kanban view")).toBeVisible();
  });

  test("should allow tasks to be created via inline form", async ({ page }) => {
    await page.goto("/");

    // 1. Click "+ Add task" in the first column (To Do)
    // We target the button specifically in the To Do column
    const todoColumn = page.locator("div", { hasText: "To Do" }).first();
    await page.getByRole("button", { name: "Add task" }).first().click();

    // 2. Fill out the form
    const testTitle = `Test Task ${Date.now()}`;
    await page.getByPlaceholder("Task title...").fill(testTitle);

    // 3. Submit (Enter)
    await page.keyboard.press("Enter");

    // 4. Verify toast success
    await expect(page.getByText("Task created")).toBeVisible();

    // 5. Verify task appears in the column
    await expect(page.getByText(testTitle)).toBeVisible();
  });
});
