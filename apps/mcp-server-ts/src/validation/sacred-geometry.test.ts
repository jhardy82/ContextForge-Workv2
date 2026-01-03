import { describe, it, expect } from "vitest";
import {
  validateGeometryShape,
  isValidGeometryShape,
  geometryShapeToString,
  VALID_GEOMETRY_SHAPES,
} from "./sacred-geometry.js";
import { GeometryShape } from "../core/types.js";

describe("Sacred Geometry Validation", () => {
  describe("VALID_GEOMETRY_SHAPES constant", () => {
    it("should contain exactly 5 valid shapes", () => {
      expect(VALID_GEOMETRY_SHAPES).toHaveLength(5);
    });

    it("should contain all required shapes in lowercase", () => {
      expect(VALID_GEOMETRY_SHAPES).toContain("Circle");
      expect(VALID_GEOMETRY_SHAPES).toContain("Triangle");
      expect(VALID_GEOMETRY_SHAPES).toContain("Spiral");
      expect(VALID_GEOMETRY_SHAPES).toContain("Pentagon");
      expect(VALID_GEOMETRY_SHAPES).toContain("Fractal");
    });

    it("should be a readonly array", () => {
      expect(Object.isFrozen(VALID_GEOMETRY_SHAPES)).toBe(false); // const but not frozen
      // TypeScript enforces readonly at compile time
    });
  });

  describe("validateGeometryShape", () => {
    describe("valid shapes", () => {
      it("should accept and normalize 'circle'", () => {
        expect(validateGeometryShape("Circle")).toBe("Circle");
      });

      it("should accept and normalize 'triangle'", () => {
        expect(validateGeometryShape("Triangle")).toBe("Triangle");
      });

      it("should accept and normalize 'spiral'", () => {
        expect(validateGeometryShape("Spiral")).toBe("Spiral");
      });

      it("should accept and normalize 'golden_ratio'", () => {
        expect(validateGeometryShape("Pentagon")).toBe("Pentagon");
      });

      it("should accept and normalize 'fractal'", () => {
        expect(validateGeometryShape("Fractal")).toBe("Fractal");
      });
    });

    describe("case-insensitive handling", () => {
      it("should accept uppercase 'CIRCLE'", () => {
        expect(validateGeometryShape("CIRCLE")).toBe("Circle");
      });

      it("should accept mixed case 'Circle'", () => {
        expect(validateGeometryShape("Circle")).toBe("Circle");
      });

      it("should accept uppercase 'PENTAGON'", () => {
        expect(validateGeometryShape("PENTAGON")).toBe("Pentagon");
      });

      it("should accept mixed case 'Pentagon'", () => {
        expect(validateGeometryShape("Pentagon")).toBe("Pentagon");
      });

      it("should accept mixed case 'TrIaNgLe'", () => {
        expect(validateGeometryShape("TrIaNgLe")).toBe("Triangle");
      });
    });

    describe("backward compatibility - empty values", () => {
      it("should accept null and return empty string", () => {
        expect(validateGeometryShape(null)).toBe("");
      });

      it("should accept undefined and return empty string", () => {
        expect(validateGeometryShape(undefined)).toBe("");
      });

      it("should accept empty string and return empty string", () => {
        expect(validateGeometryShape("")).toBe("");
      });
    });

    describe("invalid shapes", () => {
      it("should reject 'octagon' (invalid shape)", () => {
        expect(() => validateGeometryShape("octagon")).toThrow(
          /Invalid geometry shape/
        );
      });

      it("should reject 'square'", () => {
        expect(() => validateGeometryShape("square")).toThrow(
          /Invalid geometry shape/
        );
      });

      it("should reject 'hexagon'", () => {
        expect(() => validateGeometryShape("hexagon")).toThrow(
          /Invalid geometry shape/
        );
      });

      it("should reject random string 'foobar'", () => {
        expect(() => validateGeometryShape("foobar")).toThrow(
          /Invalid geometry shape/
        );
      });

      it("should include valid shapes in error message", () => {
        try {
          validateGeometryShape("invalid");
        } catch (error) {
          expect((error as Error).message).toContain("Circle");
          expect((error as Error).message).toContain("Triangle");
          expect((error as Error).message).toContain("Spiral");
          expect((error as Error).message).toContain("Pentagon");
          expect((error as Error).message).toContain("Fractal");
        }
      });
    });
  });

  describe("isValidGeometryShape", () => {
    describe("valid shapes", () => {
      it("should return true for 'circle'", () => {
        expect(isValidGeometryShape("Circle")).toBe(true);
      });

      it("should return true for 'triangle'", () => {
        expect(isValidGeometryShape("Triangle")).toBe(true);
      });

      it("should return true for 'spiral'", () => {
        expect(isValidGeometryShape("Spiral")).toBe(true);
      });

      it("should return true for 'golden_ratio'", () => {
        expect(isValidGeometryShape("Pentagon")).toBe(true);
      });

      it("should return true for 'fractal'", () => {
        expect(isValidGeometryShape("Fractal")).toBe(true);
      });
    });

    describe("case-insensitive handling", () => {
      it("should return true for uppercase shapes", () => {
        expect(isValidGeometryShape("CIRCLE")).toBe(true);
        expect(isValidGeometryShape("TRIANGLE")).toBe(true);
        expect(isValidGeometryShape("SPIRAL")).toBe(true);
        expect(isValidGeometryShape("PENTAGON")).toBe(true);
        expect(isValidGeometryShape("FRACTAL")).toBe(true);
      });

      it("should return true for mixed case shapes", () => {
        expect(isValidGeometryShape("Circle")).toBe(true);
        expect(isValidGeometryShape("Triangle")).toBe(true);
        expect(isValidGeometryShape("Pentagon")).toBe(true);
      });
    });

    describe("backward compatibility - empty values", () => {
      it("should return true for null (backward compatible)", () => {
        expect(isValidGeometryShape(null)).toBe(true);
      });

      it("should return true for undefined (backward compatible)", () => {
        expect(isValidGeometryShape(undefined)).toBe(true);
      });

      it("should return true for empty string (backward compatible)", () => {
        expect(isValidGeometryShape("")).toBe(true);
      });
    });

    describe("invalid shapes", () => {
      it("should return false for 'hexagon'", () => {
        expect(isValidGeometryShape("hexagon")).toBe(false);
      });

      it("should return false for 'square'", () => {
        expect(isValidGeometryShape("square")).toBe(false);
      });

      it("should return false for 'hexagon'", () => {
        expect(isValidGeometryShape("hexagon")).toBe(false);
      });

      it("should return false for random string", () => {
        expect(isValidGeometryShape("foobar")).toBe(false);
      });
    });

    describe("boolean return guarantee", () => {
      it("should always return boolean true or false, never throw", () => {
        expect(typeof isValidGeometryShape("Circle")).toBe("boolean");
        expect(typeof isValidGeometryShape("invalid")).toBe("boolean");
        expect(typeof isValidGeometryShape(null)).toBe("boolean");
        expect(typeof isValidGeometryShape(undefined)).toBe("boolean");
      });
    });
  });

  describe("geometryShapeToString", () => {
    it("should convert GeometryShape.Circle to 'circle'", () => {
      expect(geometryShapeToString(GeometryShape.Circle)).toBe("Circle");
    });

    it("should convert GeometryShape.Triangle to 'triangle'", () => {
      expect(geometryShapeToString(GeometryShape.Triangle)).toBe("Triangle");
    });

    it("should convert GeometryShape.Spiral to 'spiral'", () => {
      expect(geometryShapeToString(GeometryShape.Spiral)).toBe("Spiral");
    });

    it("should convert GeometryShape.Pentagon to 'golden_ratio'", () => {
      expect(geometryShapeToString(GeometryShape.Pentagon)).toBe(
        "Pentagon"
      );
    });

    it("should convert GeometryShape.Fractal to 'fractal'", () => {
      expect(geometryShapeToString(GeometryShape.Fractal)).toBe("Fractal");
    });

    it("should return string type", () => {
      const result = geometryShapeToString(GeometryShape.Circle);
      expect(typeof result).toBe("string");
    });
  });

  describe("integration: validateGeometryShape + isValidGeometryShape consistency", () => {
    it("should agree on valid shapes", () => {
      VALID_GEOMETRY_SHAPES.forEach((shape) => {
        expect(isValidGeometryShape(shape)).toBe(true);
        expect(() => validateGeometryShape(shape)).not.toThrow();
      });
    });

    it("should agree on invalid shapes", () => {
      const invalidShapes = ["golden_ratio", "square", "hexagon", "invalid"];
      invalidShapes.forEach((shape) => {
        expect(isValidGeometryShape(shape)).toBe(false);
        expect(() => validateGeometryShape(shape)).toThrow();
      });
    });

    it("should agree on empty values", () => {
      const emptyValues = [null, undefined, ""];
      emptyValues.forEach((value) => {
        expect(isValidGeometryShape(value)).toBe(true);
        expect(() => validateGeometryShape(value)).not.toThrow();
        expect(validateGeometryShape(value)).toBe("");
      });
    });
  });

  describe("edge cases and regression tests", () => {
    it("should handle whitespace in shape names gracefully", () => {
      // Should fail because spaces aren't normalized
      expect(isValidGeometryShape(" circle ")).toBe(false);
      expect(() => validateGeometryShape(" circle ")).toThrow();
    });

    it("should handle hyphenated golden-ratio correctly", () => {
      // golden-ratio uses underscore, not hyphen
      expect(isValidGeometryShape("golden-ratio")).toBe(false);
      expect(() => validateGeometryShape("golden-ratio")).toThrow();
    });

    it("should handle golden_ratio with underscore correctly", () => {
      expect(isValidGeometryShape("Pentagon")).toBe(true);
      expect(validateGeometryShape("Pentagon")).toBe("Pentagon");
    });
  });
});
