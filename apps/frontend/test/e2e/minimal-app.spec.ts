import { expect, test } from '@playwright/test';

test('minimal app renders correctly', async ({ page }) => {
  // Navigate to the app
  await page.goto('http://localhost:5176', { waitUntil: 'networkidle' });

  // Take a screenshot to see what's rendered
  await page.screenshot({ path: 'test-results/minimal-app-screenshot.png' });

  // Check if the minimal test component rendered
  const heading = page.locator('h1');
  const headingText = await heading.textContent().catch(() => 'NOT_FOUND');
  console.log('Heading text:', headingText);

  // Check the body content
  const bodyContent = await page.locator('body').innerHTML();
  console.log('Body content length:', bodyContent.length);
  console.log('First 500 chars:', bodyContent.substring(0, 500));

  // Check for console errors
  const consoleMessages: string[] = [];
  page.on('console', msg => {
    consoleMessages.push(`${msg.type()}: ${msg.text()}`);
  });

  // Reload to capture console from start
  await page.reload({ waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);

  console.log('Console messages:', consoleMessages);

  // Take another screenshot after reload
  await page.screenshot({ path: 'test-results/minimal-app-after-reload.png' });

  // Verify something rendered
  const rootContent = await page.locator('#root').innerHTML();
  console.log('Root content length:', rootContent.length);

  expect(rootContent.length).toBeGreaterThan(0);
});
