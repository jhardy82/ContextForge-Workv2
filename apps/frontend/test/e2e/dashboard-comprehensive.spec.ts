import { expect, test } from '@playwright/test';

// Define the base URL - assuming standard local dev port from previous steps
const BASE_URL = 'http://127.0.0.1:5174';

test.describe('TaskMan v3 Comprehensive Validation', () => {

    test.beforeEach(async ({ page }) => {
        await page.goto(BASE_URL);
        // Wait for connection to be established (green badge)
        await expect(page.locator('text=Connected')).toBeVisible({ timeout: 10000 });
    });

    test('Phase 5: Aurora UI Theme Applied', async ({ page }) => {
        // Feature: Artistic UI Overhaul
        // Check for the global aurora background class on the main container
        const mainContainer = page.locator('.min-h-screen.bg-aurora');
        await expect(mainContainer).toBeVisible();

        // Check for glassmorphic elements (Kanban columns)
        const kanbanCol = page.locator('.glass').first();
        await expect(kanbanCol).toBeVisible();
    });

    test('Phase 1 & 6: Task Creation & Database Persistence', async ({ page }) => {
        // Feature: Data Persistence via Docker Backend
        const taskTitle = `Sync Test ${Date.now()}`;

        // 1. Create Task
        await page.click('button:has-text("+ Add task")'); // Click add task in first column (To Do)
        await page.fill('input[placeholder="Task Title"]', taskTitle);
        await page.click('button:has-text("Add Task")'); // Submit form

        // 2. Verify it appears
        await expect(page.locator(`text=${taskTitle}`)).toBeVisible();

        // 3. Reload Page to test Persistence
        await page.reload();
        await expect(page.locator('text=Connected')).toBeVisible(); // Wait for reconnect

        // 4. Verify task persists
        await expect(page.locator(`text=${taskTitle}`)).toBeVisible();
    });

    test('Phase 3: Sprint Planning Functionality', async ({ page }) => {
        // Feature: Sprint Management

        // 1. Switch to Sprint View
        await page.click('button:has(.lucide-timer)'); // Timer icon for Sprint View

        // 2. Verify Sprint View Elements
        await expect(page.locator('text=Backlog')).toBeVisible();
        await expect(page.locator('text=Active Sprints')).toBeVisible();

        // 3. Create a New Sprint
        await page.click('button:has-text("New Sprint")');
        const sprintName = `Sprint ${Date.now()}`;
        await page.fill('input[name="name"]', sprintName);
        await page.click('button:has-text("Create Sprint")');

        // 4. Verify Sprint Created
        await expect(page.locator(`text=${sprintName}`)).toBeVisible();
    });

    test('Phase 4: Analytics View Rendering', async ({ page }) => {
        // Feature: Artistic Analytics

        // 1. Switch to Analytics View
        await page.click('button:has(.lucide-pie-chart)'); // PieChart icon for Analytics View

        // 2. Verify Header
        await expect(page.locator('text=Analytics & Insights')).toBeVisible();

        // 3. Verify Charts Rendered (Recharts uses .recharts-surface class)
        // We expect at least 3 charts: Velocity, Distribution, Rhythm
        const charts = page.locator('.recharts-surface');
        await expect(charts).toHaveCount(3);

        // 4. Verify Stat Cards
        await expect(page.locator('text=Velocity')).toBeVisible();
        await expect(page.locator('text=Completion Rate')).toBeVisible();
    });

    test('Phase 2: AI Input Presence', async ({ page }) => {
        // Feature: AI Integration (UI presence check)
        // Check if the AI input field exists
        await expect(page.locator('input[placeholder*="Ask AI to create tasks"]')).toBeVisible();
    });
});
