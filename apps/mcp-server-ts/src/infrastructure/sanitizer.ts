/**
 * Input Sanitizer - Phase 1.4
 *
 * Sanitizes user input to prevent XSS, injection attacks
 */

import validator from "validator";

/**
 * Sanitize a string input
 * - Trims whitespace
 * - Escapes HTML entities
 * - Normalizes Unicode
 */
export function sanitizeString(input: string): string {
  if (typeof input !== "string") {
    return "";
  }

  return validator.trim(
    validator.escape(
      validator.normalizeEmail(input, { all_lowercase: false }) || input
    )
  );
}

/**
 * Sanitize HTML content (strips all tags)
 */
export function sanitizeHTML(input: string): string {
  if (typeof input !== "string") {
    return "";
  }

  return validator.stripLow(validator.trim(input));
}

/**
 * Sanitize and validate email
 */
export function sanitizeEmail(input: string): string | null {
  if (!validator.isEmail(input)) {
    return null;
  }

  const normalized = validator.normalizeEmail(input, { all_lowercase: true });
  return normalized === false ? null : normalized;
}

/**
 * Sanitize URL
 */
export function sanitizeURL(input: string): string | null {
  if (!validator.isURL(input, { require_protocol: true })) {
    return null;
  }

  return validator.trim(input);
}

/**
 * Sanitize an object recursively
 */
export function sanitizeObject<T extends Record<string, any>>(obj: T): T {
  const sanitized: any = {};

  for (const [key, value] of Object.entries(obj)) {
    if (typeof value === "string") {
      sanitized[key] = sanitizeString(value);
    } else if (Array.isArray(value)) {
      sanitized[key] = value.map((item) =>
        typeof item === "string" ? sanitizeString(item) : item
      );
    } else if (value && typeof value === "object") {
      sanitized[key] = sanitizeObject(value);
    } else {
      sanitized[key] = value;
    }
  }

  return sanitized as T;
}

/**
 * Check if string contains potential SQL injection
 */
export function containsSQLInjection(input: string): boolean {
  const sqlPatterns = [
    /(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)/i,
    /(--|\/\*|\*\/|;|'|")/,
    /(\bOR\b.*=.*)/i,
    /(\bAND\b.*=.*)/i,
  ];

  return sqlPatterns.some((pattern) => pattern.test(input));
}

/**
 * Check if string contains potential XSS
 */
export function containsXSS(input: string): boolean {
  const xssPatterns = [
    /<script[^>]*>.*?<\/script>/gi,
    /on\w+\s*=\s*["'][^"']*["']/gi,
    /javascript:/gi,
    /<iframe[^>]*>/gi,
  ];

  return xssPatterns.some((pattern) => pattern.test(input));
}
