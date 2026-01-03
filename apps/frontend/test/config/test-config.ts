/**
 * Centralized Test Configuration
 * Shared configuration for all test types
 */

export interface TestConfig {
  baseUrl: string;
  timeout: number;
  retries: number;
  workers: number;
  mockApiDelay: number;
  visualThreshold: number;
  performanceThresholds: {
    loadTime: number;
    firstContentfulPaint: number;
    largestContentfulPaint: number;
    cumulativeLayoutShift: number;
    firstInputDelay: number;
    memoryIncrease: number;
  };
  accessibilityRules: string[];
}

export const testConfig: TestConfig = {
  baseUrl: process.env.BASE_URL || 'http://localhost:5173',
  timeout: 60000,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : 4,
  mockApiDelay: 100,
  visualThreshold: 0.5,
  performanceThresholds: {
    loadTime: 5000,
    firstContentfulPaint: 1800,
    largestContentfulPaint: 2500,
    cumulativeLayoutShift: 0.1,
    firstInputDelay: 100,
    memoryIncrease: 50 // percentage
  },
  accessibilityRules: [
    'wcag2a',
    'wcag2aa', 
    'wcag21aa',
    'color-contrast',
    'keyboard-navigation',
    'focus-management',
    'aria-usage',
    'semantic-markup'
  ]
};

export const mockApiResponses = {
  health: {
    connected: { connected: true, status: 'connected', version: '1.0.0' },
    disconnected: { connected: false, status: 'disconnected', error: 'Connection failed' }
  },
  projects: [
    {
      id: '1',
      name: 'Test Project Alpha',
      description: 'Primary testing project for comprehensive test suite',
      status: 'active',
      created: '2024-01-15T10:00:00Z',
      updated: '2024-01-15T15:30:00Z'
    },
    {
      id: '2',
      name: 'Test Project Beta',
      description: 'Secondary project for testing edge cases',
      status: 'inactive',
      created: '2024-01-10T08:00:00Z',
      updated: '2024-01-14T12:00:00Z'
    }
  ],
  tasks: [
    {
      id: '1',
      title: 'Critical System Integration Task',
      description: 'Ensure all system components work together seamlessly',
      status: 'new',
      priority: 'high',
      projectId: '1',
      created: '2024-01-15T09:00:00Z',
      updated: '2024-01-15T14:00:00Z',
      assignee: 'system-integrator',
      tags: ['integration', 'system', 'critical']
    },
    {
      id: '2',
      title: 'User Interface Consistency Review',
      description: 'Review and ensure UI consistency across all components',
      status: 'in-progress',
      priority: 'medium',
      projectId: '1',
      created: '2024-01-15T10:30:00Z',
      updated: '2024-01-15T16:15:00Z',
      assignee: 'ui-designer',
      tags: ['ui', 'consistency', 'design']
    },
    {
      id: '3',
      title: 'Performance Optimization Initiative',
      description: 'Optimize application performance across all metrics',
      status: 'completed',
      priority: 'low',
      projectId: '2',
      created: '2024-01-12T14:00:00Z',
      updated: '2024-01-14T11:30:00Z',
      assignee: 'performance-engineer',
      tags: ['performance', 'optimization', 'metrics']
    },
    {
      id: '4',
      title: 'Security Vulnerability Assessment',
      description: 'Comprehensive security review and vulnerability testing',
      status: 'blocked',
      priority: 'high',
      projectId: '1',
      created: '2024-01-14T16:00:00Z',
      updated: '2024-01-15T13:45:00Z',
      assignee: 'security-analyst',
      tags: ['security', 'vulnerability', 'assessment']
    },
    {
      id: '5',
      title: 'Documentation Update Sprint',
      description: 'Update all technical documentation to current standards',
      status: 'pending',
      priority: 'medium',
      projectId: '2',
      created: '2024-01-13T11:00:00Z',
      updated: '2024-01-15T09:20:00Z',
      assignee: 'tech-writer',
      tags: ['documentation', 'standards', 'update']
    }
  ]
};

export const browserViewports = {
  'mobile-sm': { width: 320, height: 568 },
  'mobile-md': { width: 375, height: 667 },
  'mobile-lg': { width: 414, height: 896 },
  'tablet-sm': { width: 768, height: 1024 },
  'tablet-lg': { width: 1024, height: 768 },
  'desktop-sm': { width: 1280, height: 720 },
  'desktop-md': { width: 1440, height: 900 },
  'desktop-lg': { width: 1920, height: 1080 },
  'desktop-xl': { width: 2560, height: 1440 }
};

export const testSelectors = {
  // Main components
  dashboard: '[data-testid="dtm-dashboard"]',
  taskList: '[data-testid="task-list"]',
  connectionStatus: '[data-testid="connection-status"]',
  
  // Interactive elements
  refreshButton: 'button[data-testid="refresh-button"]',
  settingsButton: 'button[data-testid="settings-button"]',
  
  // Modal and overlay elements
  modal: '[role="dialog"]',
  modalClose: '[data-testid="modal-close"]',
  overlay: '[data-testid="overlay"]',
  
  // Task elements
  task: '[data-testid^="task-"]',
  taskTitle: '[data-testid="task-title"]',
  taskStatus: '[data-testid="task-status"]',
  taskPriority: '[data-testid="task-priority"]',
  
  // Form elements
  searchInput: '[data-testid="search-input"]',
  filterSelect: '[data-testid="filter-select"]',
  
  // Status indicators
  loadingSpinner: '[data-testid="loading"]',
  emptyState: '[data-testid="empty-state"]',
  errorMessage: '[data-testid="error-message"]'
};

export const testData = {
  search: {
    validQueries: ['Critical', 'System', 'UI', 'Performance'],
    invalidQueries: ['xyz123', '!@#$%', ''],
    specialCharacters: ['<script>', 'DROP TABLE', '../../etc/passwd']
  },
  
  forms: {
    validInputs: {
      name: 'Test Project',
      description: 'A test project for validation',
      email: 'test@example.com',
      url: 'https://example.com'
    },
    invalidInputs: {
      name: '',
      description: 'a'.repeat(1001), // Too long
      email: 'invalid-email',
      url: 'not-a-url'
    }
  },
  
  edge_cases: {
    longText: 'Lorem ipsum '.repeat(100),
    specialCharacters: '!@#$%^&*()_+-=[]{}|;:,.<>?',
    unicode: '🚀 📊 ✅ ❌ 🎯 🔧 🎨 📋',
    numbers: '1234567890',
    whitespace: '   \t\n\r   '
  }
};

export default testConfig;