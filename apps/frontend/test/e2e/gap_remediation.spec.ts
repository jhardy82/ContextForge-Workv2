import { expect, test } from "@playwright/test";

test("Gap Remediation: Detail Panel & Settings", async ({ page }) => {
  // 1. Navigate to Dashboard
  console.log("Navigating to dashboard...");
  await page.goto("/", { timeout: 30000 });
  await expect(page.getByText("TaskMan v3")).toBeVisible();

  // 2. Test Task Detail Panel (Slide-over)
  console.log("Testing Task Detail Panel...");
  // Find a task card and click it. We assume at least one task exists (mocked or real)
  // If no tasks, we create one quickly via Command Palette to ensure test robustness
  await page.keyboard.press("Control+k");
  await page.getByPlaceholder("Type a command...").fill("Create new task");
  await page.keyboard.press("Enter");

  // Wait for Quick Task Form
  await expect(page.getByPlaceholder("Task Title")).toBeVisible();
  await page.getByPlaceholder("Task Title").fill("Test Gap Task");
  await page.keyboard.press("Enter");

  // Click the newly created task
  await page.getByText("Test Gap Task").first().click();

  // Verify Slide-over opens
  await expect(page.getByText("Task Details", { exact: true })).toBeVisible();
  await expect(page.getByLabel("Task Title")).toHaveValue("Test Gap Task");

  // Close panel
  await page.getByRole("button", { name: "Close" }).click(); // OR click outside, but close button is safer if exists.
  // Shadcn sheet usually has a generic close X.
  // Alternatively press Escape
  await page.keyboard.press("Escape");
  await expect(
    page.getByText("Task Details", { exact: true })
  ).not.toBeVisible();

  // 3. Test Settings Dialog
  console.log("Testing Settings Dialog...");
  await page.locator("button:has(.lucide-settings)").click(); // Finding the settings button by icon class if generic
  // Or finding by recent change: <Settings className="w-4 h-4" />

  await expect(page.getByRole("dialog", { name: "Settings" })).toBeVisible();
  await expect(page.getByText("Dark Mode")).toBeVisible();
  await expect(page.getByText("Clear Cache")).toBeVisible();

  // Close Settings
  await page.keyboard.press("Escape");
  await expect(
    page.getByRole("dialog", { name: "Settings" })
  ).not.toBeVisible();

  console.log("Gap Remediation Verified.");
  await page.screenshot({ path: "test-results/audit/remediation_success.png" });
});
