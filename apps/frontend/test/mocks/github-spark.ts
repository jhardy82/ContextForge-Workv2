/**
 * Mock implementation of @github/spark/hooks for testing
 */

export const useKV = (key: string, defaultValue?: any) => {
  // Create a simple state-like return for testing
  const value = defaultValue || null;
  const setValue = (newValue: any) => {
    // Mock setter that doesn't actually store anything
    console.log(`Mock useKV setValue called for key: ${key}, value:`, newValue);
  };

  return [value, setValue];
};

// Mock the global spark object for testing
if (typeof window !== "undefined") {
  (window as any).spark = {
    useKV,
    // Add other spark properties as needed
  };
}
