import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Suspense, lazy } from 'react';

// Lazy load DashboardV3 to ensure React Query provider is ready
const DashboardV3 = lazy(() => import('@/components/dashboard').then(m => ({ default: m.DashboardV3 })));

// Create a client with more lenient error handling
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 10000,
      // Add refetch on window focus false to reduce noise during debugging
      refetchOnWindowFocus: false,
    },
  },
});

// Loading fallback component
function LoadingFallback() {
  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      height: '100vh',
      background: 'linear-gradient(135deg, #1a1a2e, #16213e)',
      color: 'white',
      fontFamily: 'system-ui'
    }}>
      <div style={{ textAlign: 'center' }}>
        <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>🔄</div>
        <p>Loading TaskMan Dashboard...</p>
      </div>
    </div>
  );
}

function App() {
  console.log("[APP] Rendering with Suspense...");
  return (
    <QueryClientProvider client={queryClient}>
      <Suspense fallback={<LoadingFallback />}>
        <DashboardV3 />
      </Suspense>
    </QueryClientProvider>
  );
}

export default App;
