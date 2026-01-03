import { test, expect } from '@playwright/test';
import { DTMApiClient } from '@/lib/dtm-api';

/**
 * DTM API Integration Tests
 * Tests the DTM API client functionality with mocked server responses
 */
test.describe('DTM API Integration', () => {
  let apiClient: DTMApiClient;
  const TEST_API_URL = 'http://localhost:8000/api/v1';

  test.beforeEach(async ({ page }) => {
    apiClient = new DTMApiClient(TEST_API_URL);
    
    // Setup common mock responses
    await page.route('**/api/v1/health', async route => {
      await route.fulfill({
        json: { 
          version: '1.0.0',
          uptime: '24 hours',
          timestamp: new Date().toISOString()
        }
      });
    });
  });

  test('health check returns correct status', async ({ page }) => {
    await page.goto('/');
    
    // Test successful health check
    const status = await apiClient.checkHealth();
    
    expect(status.connected).toBe(true);
    expect(status.status).toBe('connected');
    expect(status.message).toContain('1.0.0');
    expect(status.lastChecked).toBeDefined();
  });

  test('health check handles server errors', async ({ page }) => {
    // Mock server error
    await page.route('**/api/v1/health', async route => {
      await route.fulfill({
        status: 500,
        json: { error: 'Internal server error' }
      });
    });

    await page.goto('/');
    
    const status = await apiClient.checkHealth();
    
    expect(status.connected).toBe(false);
    expect(status.status).toBe('error');
    expect(status.message).toContain('500');
  });

  test('health check handles network errors', async ({ page }) => {
    // Mock network failure
    await page.route('**/api/v1/health', async route => {
      await route.abort('internetdisconnected');
    });

    await page.goto('/');
    
    const status = await apiClient.checkHealth();
    
    expect(status.connected).toBe(false);
    expect(status.status).toBe('disconnected');
    expect(status.message).toBeDefined();
  });

  test('projects API returns correct data structure', async ({ page }) => {
    const mockProjects = [
      {
        id: 'P-TEST-001',
        name: 'Project Alpha',
        description: 'First test project',
        status: 'active',
        created_at: '2024-01-01T00:00:00Z'
      },
      {
        id: 'P-TEST-002',
        name: 'Project Beta',
        description: 'Second test project',
        status: 'completed',
        created_at: '2024-01-02T00:00:00Z'
      }
    ];

    await page.route('**/api/v1/projects', async route => {
      await route.fulfill({
        json: mockProjects
      });
    });

    await page.goto('/');
    
    const projects = await apiClient.getProjects();
    
    expect(projects).toHaveLength(2);
    expect(projects[0].id).toBe('P-TEST-001');
    expect(projects[0].name).toBe('Project Alpha');
    expect(projects[0].status).toBe('active');
    expect(projects[1].status).toBe('completed');
  });

  test('projects API handles empty response', async ({ page }) => {
    await page.route('**/api/v1/projects', async route => {
      await route.fulfill({
        json: []
      });
    });

    await page.goto('/');
    
    const projects = await apiClient.getProjects();
    
    expect(projects).toHaveLength(0);
    expect(Array.isArray(projects)).toBe(true);
  });

  test('projects API falls back to sample data on error', async ({ page }) => {
    await page.route('**/api/v1/projects', async route => {
      await route.fulfill({
        status: 404,
        json: { error: 'Projects not found' }
      });
    });

    await page.goto('/');
    
    const projects = await apiClient.getProjects();
    
    // Should return sample data when API fails
    expect(projects.length).toBeGreaterThan(0);
    expect(projects[0].id).toContain('P-');
  });

  test('tasks API returns correct data structure', async ({ page }) => {
    const mockTasks = [
      {
        id: 'T-TEST-001',
        title: 'Implement feature X',
        description: 'Add new feature X to the application',
        status: 'new',
        priority: 'high',
        shape: 'Triangle',
        project_id: 'P-TEST-001',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z'
      },
      {
        id: 'T-TEST-002',
        title: 'Fix bug Y',
        description: 'Resolve critical bug Y',
        status: 'in_progress',
        priority: 'critical',
        shape: 'Circle',
        project_id: 'P-TEST-001',
        created_at: '2024-01-02T00:00:00Z',
        updated_at: '2024-01-02T12:00:00Z'
      }
    ];

    await page.route('**/api/v1/tasks', async route => {
      await route.fulfill({
        json: mockTasks
      });
    });

    await page.goto('/');
    
    const tasks = await apiClient.getTasks();
    
    expect(tasks).toHaveLength(2);
    expect(tasks[0].id).toBe('T-TEST-001');
    expect(tasks[0].title).toBe('Implement feature X');
    expect(tasks[0].status).toBe('new');
    expect(tasks[0].priority).toBe('high');
    expect(tasks[0].shape).toBe('Triangle');
    expect(tasks[1].status).toBe('in_progress');
    expect(tasks[1].priority).toBe('critical');
  });

  test('tasks API falls back to sample data on error', async ({ page }) => {
    await page.route('**/api/v1/tasks', async route => {
      await route.fulfill({
        status: 500,
        json: { error: 'Internal server error' }
      });
    });

    await page.goto('/');
    
    const tasks = await apiClient.getTasks();
    
    // Should return sample data when API fails
    expect(tasks.length).toBeGreaterThan(0);
    expect(tasks[0].id).toContain('T-');
  });

  test('single task API returns detailed data', async ({ page }) => {
    const mockTask = {
      id: 'T-TEST-001',
      title: 'Detailed task',
      description: 'A task with full details',
      status: 'in_progress',
      priority: 'medium',
      shape: 'Triangle',
      project_id: 'P-TEST-001',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T12:00:00Z'
    };

    await page.route('**/api/v1/tasks/T-TEST-001', async route => {
      await route.fulfill({
        json: mockTask
      });
    });

    await page.goto('/');
    
    const task = await apiClient.getTask('T-TEST-001');
    
    expect(task).not.toBeNull();
    expect(task!.id).toBe('T-TEST-001');
    expect(task!.title).toBe('Detailed task');
    expect(task!.status).toBe('in_progress');
    expect(task!.shape).toBe('Triangle');
  });

  test('single task API returns null for non-existent task', async ({ page }) => {
    await page.route('**/api/v1/tasks/NON-EXISTENT', async route => {
      await route.fulfill({
        status: 404,
        json: { error: 'Task not found' }
      });
    });

    await page.goto('/');
    
    const task = await apiClient.getTask('NON-EXISTENT');
    
    expect(task).toBeNull();
  });

  test('AI prompt generation works correctly', async ({ page }) => {
    await page.goto('/');
    
    const mockTask = {
      id: 'T-TEST-001',
      title: 'Test Task',
      description: 'A test task for prompt generation',
      status: 'new' as const,
      priority: 'high' as const,
      shape: 'Triangle' as const,
      project_id: 'P-TEST-001',
      created_at: '2024-01-01T00:00:00Z'
    };

    // Test implementation prompt
    const implPrompt = apiClient.generateAIPrompt(mockTask, 'implementation');
    expect(implPrompt).toContain('Test Task');
    expect(implPrompt).toContain('implementation guidance');
    expect(implPrompt).toContain('Triangle');

    // Test testing prompt
    const testPrompt = apiClient.generateAIPrompt(mockTask, 'testing');
    expect(testPrompt).toContain('Test Task');
    expect(testPrompt).toContain('test cases');

    // Test validation prompt
    const validationPrompt = apiClient.generateAIPrompt(mockTask, 'validation');
    expect(validationPrompt).toContain('Test Task');
    expect(validationPrompt).toContain('validation criteria');
  });

  test('connection status tracking works', async ({ page }) => {
    await page.goto('/');
    
    // Initially disconnected
    expect(apiClient.isConnected()).toBe(false);
    
    // After successful health check
    await apiClient.checkHealth();
    expect(apiClient.isConnected()).toBe(true);
    
    // After failed health check
    await page.route('**/api/v1/health', async route => {
      await route.fulfill({
        status: 500,
        json: { error: 'Server error' }
      });
    });
    
    await apiClient.checkHealth();
    expect(apiClient.isConnected()).toBe(false);
  });

  test('API client handles timeout correctly', async ({ page }) => {
    await page.route('**/api/v1/tasks', async route => {
      // Simulate slow response (longer than 10s timeout)
      await new Promise(resolve => setTimeout(resolve, 15000));
      await route.fulfill({ json: [] });
    });

    await page.goto('/');
    
    // Should return fallback data due to timeout
    const tasks = await apiClient.getTasks();
    expect(Array.isArray(tasks)).toBe(true);
    expect(tasks.length).toBeGreaterThan(0); // Sample data
  });

  test('API client handles malformed JSON responses', async ({ page }) => {
    await page.route('**/api/v1/tasks', async route => {
      await route.fulfill({
        body: '{ invalid json }',
        headers: { 'Content-Type': 'application/json' }
      });
    });

    await page.goto('/');
    
    // Should return fallback data
    const tasks = await apiClient.getTasks();
    expect(Array.isArray(tasks)).toBe(true);
    expect(tasks.length).toBeGreaterThan(0); // Sample data
  });

  test('API client handles different response formats', async ({ page }) => {
    // Test wrapped response format
    await page.route('**/api/v1/tasks', async route => {
      await route.fulfill({
        json: {
          data: [
            {
              id: 'T-WRAPPED-001',
              title: 'Wrapped Task',
              status: 'new',
              created_at: '2024-01-01T00:00:00Z'
            }
          ],
          success: true,
          message: 'Tasks retrieved successfully'
        }
      });
    });

    await page.goto('/');
    
    const tasks = await apiClient.getTasks();
    
    expect(tasks).toHaveLength(1);
    expect(tasks[0].id).toBe('T-WRAPPED-001');
    expect(tasks[0].title).toBe('Wrapped Task');
  });

  test('sample data generation provides consistent structure', async ({ page }) => {
    await page.goto('/');
    
    // Force offline mode by failing health check
    await page.route('**/api/v1/health', async route => {
      await route.abort('internetdisconnected');
    });
    
    await apiClient.checkHealth();
    
    const projects = await apiClient.getProjects();
    const tasks = await apiClient.getTasks();
    
    // Verify sample data structure
    expect(projects.length).toBeGreaterThan(0);
    expect(tasks.length).toBeGreaterThan(0);
    
    // Check project structure
    expect(projects[0]).toHaveProperty('id');
    expect(projects[0]).toHaveProperty('name');
    expect(projects[0]).toHaveProperty('status');
    expect(projects[0]).toHaveProperty('created_at');
    
    // Check task structure
    expect(tasks[0]).toHaveProperty('id');
    expect(tasks[0]).toHaveProperty('title');
    expect(tasks[0]).toHaveProperty('status');
    expect(tasks[0]).toHaveProperty('priority');
    expect(tasks[0]).toHaveProperty('shape');
    expect(tasks[0]).toHaveProperty('created_at');
  });

  test('API client provides consistent error handling', async ({ page }) => {
    const errorScenarios = [
      { status: 400, error: 'Bad Request' },
      { status: 401, error: 'Unauthorized' },
      { status: 403, error: 'Forbidden' },
      { status: 404, error: 'Not Found' },
      { status: 500, error: 'Internal Server Error' },
      { status: 503, error: 'Service Unavailable' }
    ];

    await page.goto('/');

    for (const scenario of errorScenarios) {
      await page.route('**/api/v1/tasks', async route => {
        await route.fulfill({
          status: scenario.status,
          json: { error: scenario.error }
        });
      });

      const tasks = await apiClient.getTasks();
      
      // Should always return array, even on error (fallback to sample data)
      expect(Array.isArray(tasks)).toBe(true);
      expect(tasks.length).toBeGreaterThan(0);
    }
  });

  test('concurrent API calls work correctly', async ({ page }) => {
    let requestCount = 0;
    
    await page.route('**/api/v1/**', async route => {
      requestCount++;
      const delay = Math.random() * 100; // Random delay 0-100ms
      await new Promise(resolve => setTimeout(resolve, delay));
      
      if (route.request().url().includes('/projects')) {
        await route.fulfill({ json: [{ id: 'P-1', name: 'Project 1', status: 'active', created_at: '2024-01-01T00:00:00Z' }] });
      } else if (route.request().url().includes('/tasks')) {
        await route.fulfill({ json: [{ id: 'T-1', title: 'Task 1', status: 'new', created_at: '2024-01-01T00:00:00Z' }] });
      } else if (route.request().url().includes('/health')) {
        await route.fulfill({ json: { version: '1.0.0', uptime: '1h' } });
      }
    });

    await page.goto('/');

    // Make concurrent calls
    const [health, projects, tasks] = await Promise.all([
      apiClient.checkHealth(),
      apiClient.getProjects(),
      apiClient.getTasks()
    ]);

    expect(health.connected).toBe(true);
    expect(projects).toHaveLength(1);
    expect(tasks).toHaveLength(1);
    expect(requestCount).toBe(3);
  });
});