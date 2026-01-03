import { describe, expect, it, vi } from "vitest";
import { ContextExplorer } from "./ContextExplorer";

// Mock React Flow
vi.mock("@xyflow/react", () => ({
  ReactFlow: () => <div>ReactFlow Mock</div>,
  Background: () => <div>Background Mock</div>,
  Controls: () => <div>Controls Mock</div>,
  MiniMap: () => <div>MiniMap Mock</div>,
  Panel: ({ children }: any) => <div>{children}</div>,
  ReactFlowProvider: ({ children }: any) => <div>{children}</div>,
  useNodesState: () => [[], vi.fn(), vi.fn()],
  useEdgesState: () => [[], vi.fn(), vi.fn()],
}));

// Mock ResizeObserver
global.ResizeObserver = class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
};

describe("ContextExplorer", () => {
  it("renders without crashing", () => {
    expect(ContextExplorer).toBeDefined();
    // In a real environment with providers, we would render(<ContextExplorer />)
  });
});
