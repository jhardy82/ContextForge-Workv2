import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

test.describe("TaskMan v3 QA Audit", () => {
  test("Page Structure & Accessibility Scan", async ({ page }) => {
    await page.goto("/");

    // 1. Snapshot: Initial Load (Kanban)
    await expect(page.getByText("TaskMan v3")).toBeVisible();
    await page.screenshot({
      path: "test-results/audit/01-dashboard-load.png",
      fullPage: true,
    });

    // 2. Accessibility Scan (Soft)
    try {
      const accessibilityScanResults = await new AxeBuilder({ page }).analyze();
      console.log(
        "A11y Violations:",
        accessibilityScanResults.violations.length
      );
      const fs = require("fs");
      if (!fs.existsSync("test-results/audit"))
        fs.mkdirSync("test-results/audit", { recursive: true });
      fs.writeFileSync(
        "test-results/audit/a11y-scan.json",
        JSON.stringify(accessibilityScanResults.violations, null, 2)
      );
    } catch (e) {
      console.error("A11y Scan Failed:", e);
    }
  });

  test("Core Workflow: Create, Navigate, Context Actions", async ({ page }) => {
    // A. Setup
    await page.goto("/");
    const taskTitle = `Audit Task ${Date.now()}`;

    // B. Navigation Checks (Top Nav)
    await test.step("Navigation", async () => {
      // Switch to Sprints
      await page.getByText("Sprints").click();
      await expect(page.getByText("Sprint Planning")).toBeVisible(); // Assuming SprintView has this
      await page.screenshot({ path: "test-results/audit/02-view-sprints.png" });

      // Switch to Analytics
      await page.getByText("Analytics").click();
      await expect(page.getByText("Analytics & Insights")).toBeVisible();
      await page.screenshot({
        path: "test-results/audit/03-view-analytics.png",
      });

      // Switch back to Kanban
      await page.getByText("Kanban").click();
    });

    // C. Create Task
    await test.step("Create Task", async () => {
      // Open Quick Create (via command palette shortcut 'C' if possible, or + button)
      // Let's use the explicit UI button if available, but QuickTaskForm usually requires state trigger.
      // DashboardV3 passes setQuickCreateStatus via `CommandPalette` -> `onCreateTask`.
      // Let's use Command Palette to be safe: Cmd+K -> "Create new task"
      await page.keyboard.press("Control+k");
      await page
        .getByPlaceholder("Type a command or search...")
        .fill("Create new task");
      await page.keyboard.press("Enter");

      // Fill Form
      await expect(page.getByPlaceholder("Task title...")).toBeVisible();
      await page.getByPlaceholder("Task title...").fill(taskTitle);
      await page.getByRole("button", { name: "Add" }).click();

      // Verify on Board
      await expect(page.getByText(taskTitle)).toBeVisible();
      await page.screenshot({ path: "test-results/audit/04-task-created.png" });
    });

    // D. Context Menu Actions (Delete, Move)
    await test.step("Context Menu", async () => {
      const card = page
        .locator(".group.bg-card")
        .filter({ hasText: taskTitle })
        .first();

      // Right click
      await card.click({ button: "right" });
      await expect(page.getByText("AI CONSTALLATION")).toBeVisible(); // Verify menu matches code
      await page.screenshot({ path: "test-results/audit/05-context-menu.png" });

      // Test Duplicate
      await page.getByText("Duplicate").click();
      await expect(page.getByText(`${taskTitle} (Copy)`)).toBeVisible();

      // Cleanup: Delete the copy
      const copyCard = page
        .locator(".group.bg-card")
        .filter({ hasText: `${taskTitle} (Copy)` })
        .first();
      await copyCard.click({ button: "right" });
      await page.getByText("Delete Task").click();
      await expect(page.getByText(`${taskTitle} (Copy)`)).not.toBeVisible();
    });

    // E. Visual Hierarchy & Missing Features (Evidence of Gaps)
    await test.step("Gap Analysis", async () => {
      const card = page
        .locator(".group.bg-card")
        .filter({ hasText: taskTitle })
        .first();

      // 1. Try to open Details (Click)
      await card.click();
      // Wait see if anything happens (Snapshot)
      await page.waitForTimeout(500);
      await page.screenshot({
        path: "test-results/audit/06-click-details-no-op.png",
      });
      // Assertion: We EXPECT this to fail if we were strict, but for audit we just record it.
      // We know from code analysis invalidation that no modal appears.

      // 2. Settings
      await page
        .getByRole("button")
        .filter({ has: page.locator(".lucide-settings") })
        .click(); // Settings Icon
      await page.waitForTimeout(500);
      await page.screenshot({
        path: "test-results/audit/07-settings-no-op.png",
      });
    });
  });
});
