import { expect, test } from '@playwright/test';

test('sanity check', async ({ page }) => {
  console.log('Starting sanity check...');
  await page.goto('https://example.com');
  const title = await page.title();
  console.log(`Page title: ${title}`);
  expect(title).toContain('Example');
});
