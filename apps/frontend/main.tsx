import { createRoot } from 'react-dom/client';
import './index.css';

import { Component, ErrorInfo, ReactNode } from 'react';

class ErrorBoundary extends Component<{ children: ReactNode }, { hasError: boolean; error: Error | null }> {
  constructor(props: { children: ReactNode }) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("Uncaught error:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="p-4 bg-red-50 text-red-900">
          <h1 className="text-xl font-bold">Something went wrong.</h1>
          <pre className="mt-2 text-sm whitespace-pre-wrap">{this.state.error?.toString()}</pre>
          <pre className="mt-2 text-xs text-gray-500">{this.state.error?.stack}</pre>
        </div>
      );
    }

    return this.props.children;
  }
}

import App from './App';

console.log("[MAIN] Starting mount...");
const rootElement = document.getElementById('root');
if (!rootElement) {
    console.error("[MAIN] CRITICAL: #root element not found!");
} else {
    try {
        const root = createRoot(rootElement);
        root.render(
            <ErrorBoundary>
                <App />
            </ErrorBoundary>
        );
        console.log("[MAIN] App Mount called.");
    } catch (e) {
        console.error("[MAIN] Error:", e);
    }
}
