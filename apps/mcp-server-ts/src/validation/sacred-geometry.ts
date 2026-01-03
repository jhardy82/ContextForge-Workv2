import { GeometryShape } from "../core/types.js";

export const VALID_GEOMETRY_SHAPES = [
  "Circle",
  "Triangle",
  "Spiral",
  "Pentagon",
  "Fractal",
] as const;

export type ValidGeometryShape = (typeof VALID_GEOMETRY_SHAPES)[number];

/**
 * Normalize geometry shape value to match backend API expectations
 * Accepts any case (e.g., "spiral", "SPIRAL", "Spiral") and normalizes to capitalized form
 */
export function validateGeometryShape(
  shape: string | null | undefined
): string {
  if (!shape || shape === "") {
    return ""; // Empty is valid (backward compatibility)
  }

  // Normalize to capitalized first letter (backend expects: "Spiral", "Circle", etc.)
  const normalized = shape.charAt(0).toUpperCase() + shape.slice(1).toLowerCase();

  if (!VALID_GEOMETRY_SHAPES.includes(normalized as ValidGeometryShape)) {
    throw new Error(
      `Invalid geometry shape: ${shape}. Valid shapes: ${VALID_GEOMETRY_SHAPES.join(", ")}`
    );
  }

  return normalized;
}

export function isValidGeometryShape(
  shape: string | null | undefined
): boolean {
  if (!shape || shape === "") {
    return true; // Empty is valid
  }

  const normalized = shape.charAt(0).toUpperCase() + shape.slice(1).toLowerCase();
  return VALID_GEOMETRY_SHAPES.includes(normalized as ValidGeometryShape);
}

export function geometryShapeToString(shape: GeometryShape): string {
  return shape.toString();
}
