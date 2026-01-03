// Test runner configuration for comprehensive testing
export const testRunnerConfig = {
  // Test execution settings
  execution: {
    timeout: 30000, // 30 seconds default timeout
    retries: 2, // Retry failed tests twice
    parallel: true, // Run tests in parallel
    maxConcurrency: 4, // Limit concurrent workers
  },

  // Coverage thresholds
  coverage: {
    global: {
      statements: 80,
      branches: 80,
      functions: 80,
      lines: 80,
    },
    perFile: {
      statements: 70,
      branches: 70,
      functions: 70,
      lines: 70,
    },
  },

  // Test patterns
  patterns: {
    unit: ['src/**/*.{test,spec}.{js,ts,jsx,tsx}'],
    integration: ['src/test/integration/**/*.{test,spec}.{js,ts,jsx,tsx}'],
    e2e: ['src/test/e2e/**/*.spec.{js,ts}'],
    visual: ['src/test/visual/**/*.spec.{js,ts}'],
    accessibility: ['src/test/accessibility/**/*.spec.{js,ts}'],
    performance: ['src/test/performance/**/*.spec.{js,ts}'],
    smoke: ['src/test/smoke/**/*.{test,spec}.{js,ts,jsx,tsx}'],
  },

  // Reporting
  reports: {
    formats: ['html', 'json', 'lcov', 'text'],
    outputDir: './test-results',
    generateSummary: true,
    includeTimestamps: true,
  },

  // Performance budgets
  performance: {
    pageLoadTime: 3000, // 3 seconds
    interactionTime: 500, // 500ms
    memoryUsage: 50 * 1024 * 1024, // 50MB
    bundleSize: 5 * 1024 * 1024, // 5MB
  },

  // Accessibility standards
  accessibility: {
    standard: 'WCAG21AA',
    includeRules: [
      'wcag2a',
      'wcag2aa',
      'wcag21aa',
      'color-contrast',
      'keyboard-navigation',
      'focus-management',
    ],
    excludeRules: [], // Rules to skip if any
  },

  // Visual regression settings
  visual: {
    threshold: 0.1, // 10% difference threshold
    animations: 'disabled',
    fullPage: true,
    retries: 3,
    viewports: {
      mobile: { width: 375, height: 667 },
      tablet: { width: 768, height: 1024 },
      desktop: { width: 1920, height: 1080 },
    },
  },

  // Test environment setup
  environment: {
    jsdom: {
      url: 'http://localhost:5173',
      userAgent: 'jsdom/test-runner',
    },
    globals: {
      IS_TEST: true,
      VERBOSE_TESTS: process.env.VERBOSE_TESTS === 'true',
    },
  },
};

export default testRunnerConfig;