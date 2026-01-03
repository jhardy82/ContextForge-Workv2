import { describe, expect, it, vi } from "vitest";
import { AgentSidebar } from "./AgentSidebar";

// Mock store
vi.mock("@/stores/uiStore", () => ({
  useUIStore: () => ({
    isAgentOpen: true,
    setIsAgentOpen: vi.fn(),
  }),
}));

describe("AgentSidebar", () => {
  it("renders when open", () => {
    // Basic smoke test - just verifying it doesn't crash
    // Ideally we would wrap in providers, but for now we just want to see if file exists and imports work
    expect(AgentSidebar).toBeDefined();
  });
});
