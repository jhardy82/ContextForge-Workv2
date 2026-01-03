import { expect, test } from "@playwright/test";
import { v4 as uuidv4 } from "uuid";

test.describe("TaskMan V3 User Journey", () => {
  test("Create task via Command Palette and Verify in Explorer", async ({
    page,
  }) => {
    const taskTitle = `Auto-Test Task ${uuidv4().substring(0, 8)}`;

    // 1. Load Dashboard
    await page.goto("/");
    await expect(page.getByText("TaskMan v3")).toBeVisible();

    // 2. Open Command Palette (Cmd+K)
    await page.keyboard.press("Control+k"); // Use Control+K for Windows (mostly safe default, or Command+K)
    // Alternatively, click the search button if shortcut is flaky in headless
    // await page.getByRole('button', { name: 'Search...' }).click();

    await expect(
      page.getByPlaceholder("Type a command or search...")
    ).toBeVisible();

    // 3. Trigger "Create new task"
    // In the palette, type "Create" or just click the item
    await page
      .getByPlaceholder("Type a command or search...")
      .fill("Create new task");
    await page.keyboard.press("Enter");

    // 4. Fill Quick Task Form
    // Assuming hitting "Create new task" usually defaults to 'todo' column input or similar
    // We need to look for the input that appears.
    // Based on analysis, DashboardV3 likely renders QuickTaskForm when quickCreateStatus is set.
    const titleInput = page.getByPlaceholder("Task title...");
    await expect(titleInput).toBeVisible();
    await titleInput.fill(taskTitle);

    // Set Priority
    // Check QuickTaskForm.tsx: Select trigger has placeholder "Priority"
    // We might need to handle the Select component interaction if we want to change it,
    // but default is fine for now, or we can try.
    // Let's stick to default Medium for stability, or try High.

    // Submit
    await page.getByRole("button", { name: "Add" }).click();

    // 5. Verify in Kanban
    // Wait for the card to appear
    const taskCard = page
      .locator(".group.bg-card")
      .filter({ hasText: taskTitle });
    await expect(taskCard).toBeVisible();

    // 6. Switch to Data Explorer via Command Palette
    await page.keyboard.press("Control+k");
    await page
      .getByPlaceholder("Type a command or search...")
      .fill("Switch to Data Explorer");
    await page.keyboard.press("Enter");

    // 7. Verify in Data Explorer
    await expect(page.getByText("Data Explorer")).toBeVisible();
    // Check if the task title exists in the table
    await expect(page.getByRole("cell", { name: taskTitle })).toBeVisible();

    // 8. Switch to Analytics View via Command Palette
    await page.keyboard.press("Control+k");
    await page
      .getByPlaceholder("Type a command or search...")
      .fill("Switch to Analytics");
    await page.keyboard.press("Enter");

    // 9. Verify Analytics View
    // Looking for a unique element from AnalyticsView.tsx
    // Based on implementation plan, it has charts and "Sacred Geometry"
    // Let's check for a heading or the view container
    await expect(page.getByText("Analytics & Insights")).toBeVisible();
  });

  test("Kanban Column interaction (smoke)", async ({ page }) => {
    await page.goto("/");
    // Locate Todo column
    await expect(page.getByText("To Do")).toBeVisible();
    // Check for "Add Task" button at bottom of col
    await expect(
      page.getByRole("button", { name: "Add Task" }).first()
    ).toBeVisible();
  });
});
