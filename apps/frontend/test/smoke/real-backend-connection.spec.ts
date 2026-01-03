import { expect, test } from "@playwright/test";

test.describe("Backend Connectivity", () => {
  test("should establish real connection to backend API", async ({ page }) => {
    // Navigate to homepage
    await page.goto("/");

    // Wait for the main dashboard to load (title check)
    await expect(page).toHaveTitle(/TaskMan/);

    // Wait for the projects API call to complete successfully
    const response = await page.waitForResponse(
      (resp) =>
        resp.url().includes("/api/v1/projects") &&
        resp.status() >= 200 &&
        resp.status() < 300,
      { timeout: 10000 }
    );

    expect(response.ok()).toBeTruthy();
  });
});
