import { GreenfieldLayoutQuery } from '@/components/GreenfieldLayoutQuery';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Component, ReactNode } from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';

// 1. Setup Query Client
const queryClient = new QueryClient();

// 2. Simple Error Boundary for Greenfield
class GreenfieldErrorBoundary extends Component<{ children: ReactNode }, { hasError: boolean; error: Error | null }> {
  constructor(props: { children: ReactNode }) {
    super(props);
    this.state = { hasError: false, error: null };
  }
  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }
  render() {
    if (this.state.hasError) {
      return (
        <div className="p-8 bg-red-950 text-red-200 min-h-screen">
          <h1 className="text-3xl font-bold mb-4">Greenfield Render Crash</h1>
          <pre className="bg-black p-4 rounded overflow-auto border border-red-800">
            {this.state.error?.toString()}
            <br />
            {this.state.error?.stack}
          </pre>
        </div>
      );
    }
    return this.props.children;
  }
}

// 3. Mount Logic
const rootEl = document.getElementById('root');
if (rootEl) {
  console.log("[GREENFIELD] Mounting GreenfieldLayout...");
  try {
    createRoot(rootEl).render(
      <GreenfieldErrorBoundary>
        <QueryClientProvider client={queryClient}>
          <GreenfieldLayoutQuery />
        </QueryClientProvider>
      </GreenfieldErrorBoundary>
    );
  } catch (err: unknown) {
    console.error("[GREENFIELD] Critical Mount Error:", err);
    if (rootEl) {
      rootEl.innerHTML = `<div style="color:red;font-weight:bold;padding:20px;">CRITICAL MOUNT ERROR: ${String(err)}</div>`;
    }
  }
} else {
  console.error("[GREENFIELD] Missing root element");
}
