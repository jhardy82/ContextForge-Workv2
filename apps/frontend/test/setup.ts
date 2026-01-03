/**
 * Vitest Test Setup for TaskMan-v2
 *
 * React 19 + @testing-library/react v16 Compatibility Fix
 * ─────────────────────────────────────────────────────────────────────
 * React 19 moved `act` from `React.act` to a named export: `import { act } from 'react'`
 * @testing-library/react v16.3.0 checks `React.act` first, then falls back to test-utils.
 * Both are unavailable in React 19, so we polyfill `React.act` here.
 */

// Set React test environment flag
;(globalThis as any).IS_REACT_ACT_ENVIRONMENT = true

// Polyfill React.act for @testing-library/react v16 compatibility with React 19
import * as React from 'react'
import { act } from 'react'
;(React as any).act = act

import '@testing-library/jest-dom'
import { expect, afterEach, beforeAll } from 'vitest'
import { cleanup } from '@testing-library/react'
import * as matchers from '@testing-library/jest-dom/matchers'

// Extend Vitest's expect with jest-dom matchers
expect.extend(matchers)

// Global test setup
beforeAll(() => {
  // Mock spark global object for tests
  Object.defineProperty(window, 'spark', {
    value: {
      llmPrompt: (strings: string[], ...values: any[]) => 
        strings.reduce((acc, str, i) => acc + str + (values[i] || ''), ''),
      llm: async (prompt: string, modelName?: string, jsonMode?: boolean) => 
        jsonMode ? '{"result": "mock"}' : 'mock response',
      user: async () => ({
        avatarUrl: 'https://github.com/user.png',
        email: 'test@example.com',
        id: 'test-user-id',
        isOwner: true,
        login: 'testuser'
      }),
      kv: {
        keys: async () => ['test-key'],
        get: async (key: string) => ({ testData: 'mock value' }),
        set: async (key: string, value: any) => {},
        delete: async (key: string) => {}
      }
    },
    writable: true
  })

  // Mock navigation API
  Object.defineProperty(window, 'navigator', {
    value: {
      ...window.navigator,
      clipboard: {
        writeText: async (text: string) => {}
      }
    },
    writable: true
  })

  // Mock ResizeObserver
  global.ResizeObserver = class ResizeObserver {
    observe() {}
    unobserve() {}
    disconnect() {}
  }

  // Mock IntersectionObserver
  global.IntersectionObserver = class IntersectionObserver {
    root = null
    rootMargin = '0px'
    thresholds = [0]
    
    constructor() {}
    observe() {}
    unobserve() {}
    disconnect() {}
    takeRecords() { return [] }
  }
})

// Cleanup after each test
afterEach(() => {
  cleanup()
})