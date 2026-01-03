/// <reference types="vite/client" />
/// <reference types="vitest/globals" />

// Extend global interface for Spark API
declare global {
  interface Window {
    spark: {
      llmPrompt: (strings: string[], ...values: any[]) => string;
      llm: (prompt: string, modelName?: string, jsonMode?: boolean) => Promise<string>;
      user: () => Promise<{
        avatarUrl: string;
        email: string;
        id: string;
        isOwner: boolean;
        login: string;
      }>;
      kv: {
        keys: () => Promise<string[]>;
        get: <T>(key: string) => Promise<T | undefined>;
        set: <T>(key: string, value: T) => Promise<void>;
        delete: (key: string) => Promise<void>;
      };
    };
  }

  // Global spark object for tests
  var spark: Window['spark'];
}

export {};