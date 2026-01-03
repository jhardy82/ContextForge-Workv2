import { render } from "@testing-library/react";
import { describe, it, expect } from "vitest";

describe("test utils", () => {
  it("renders simple component", () => {
    render(<div>Hello Test</div>);
  });
});
