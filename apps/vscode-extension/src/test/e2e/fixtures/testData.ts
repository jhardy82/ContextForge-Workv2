/**
 * E2E Test Fixtures
 * Sample data for E2E tests
 */

export const mockTasks = [
  {
    id: 'test-task-1',
    title: 'Test Task 1',
    completed: false,
    group: 'Default',
    description: 'This is a test task',
    dueDate: new Date(Date.now() + 86400000).toISOString(), // Tomorrow
    tags: ['test', 'e2e'],
  },
  {
    id: 'test-task-2',
    title: 'Test Task 2',
    completed: true,
    group: 'Default',
    description: 'This is a completed test task',
    tags: ['test'],
  },
  {
    id: 'test-task-3',
    title: 'Overdue Task',
    completed: false,
    group: 'Urgent',
    description: 'This task is overdue',
    dueDate: new Date(Date.now() - 86400000).toISOString(), // Yesterday
    tags: ['urgent', 'overdue'],
  },
];

export const mockProjects = [
  {
    id: 'proj-1',
    name: 'Test Project',
    description: 'A test project',
    status: 'active',
  },
];

export const mockSprints = [
  {
    id: 'sprint-1',
    name: 'Sprint 1',
    projectId: 'proj-1',
    status: 'active',
    startDate: new Date(Date.now() - 604800000).toISOString(), // 1 week ago
    endDate: new Date(Date.now() + 604800000).toISOString(), // 1 week from now
  },
];

export const mockDTMResponse = {
  health: {
    status: 'healthy',
    version: '1.0.0',
    database: 'connected',
  },
  tasks: mockTasks,
  projects: mockProjects,
  sprints: mockSprints,
};

export const mockDatabaseConfig = {
  host: 'localhost',
  port: 5432,
  database: 'taskman_test',
  user: 'test_user',
  password: 'test_password',
};

export const mockSettings = {
  dtmApiUrl: 'http://localhost:3001/api',
  dtmServerPort: 3001,
  autoSync: true,
  syncInterval: 60000,
  databaseMode: 'api',
};
