import { describe, it, expect } from "vitest";
import { createStdioTransportPlaceholder } from "./stdio.js";

describe("stdio transport placeholder", () => {
  it("should return placeholder string", () => {
    const result = createStdioTransportPlaceholder();
    expect(result).toBe("stdio transport placeholder");
  });

  it("should return string type", () => {
    const result = createStdioTransportPlaceholder();
    expect(typeof result).toBe("string");
  });

  it("should be consistent across multiple calls", () => {
    const result1 = createStdioTransportPlaceholder();
    const result2 = createStdioTransportPlaceholder();
    expect(result1).toBe(result2);
  });
});
