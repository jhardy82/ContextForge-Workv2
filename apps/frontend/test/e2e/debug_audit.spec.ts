import { test } from "@playwright/test";

test("Debug Screenshot", async ({ page }) => {
  console.log("Navigating...");
  await page.goto("/", { timeout: 30000 });
  console.log("Navigated. Taking Dashboard screenshot...");
  await page.screenshot({ path: "test-results/audit/dashboard.png" });

  // Analytics
  await page.getByText("Analytics").click();
  await expect(page.getByText("Analytics & Insights")).toBeVisible();
  await page.screenshot({ path: "test-results/audit/analytics.png" });
  console.log("Screenshots saved.");
});
