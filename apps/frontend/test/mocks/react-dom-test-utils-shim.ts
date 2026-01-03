/**
 * React 19 Compatibility Shim for react-dom/test-utils
 *
 * React 19 removed the react-dom/test-utils module. This shim re-exports
 * the `act` function from the `react` package to maintain compatibility
 * with @testing-library/react v16 which still imports from test-utils.
 *
 * This shim is mapped via Vite's resolve.alias configuration.
 */

export { act } from 'react'
