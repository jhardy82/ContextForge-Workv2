/**
 * Error Normalization Utilities
 *
 * Centralizes error handling across all API calls for consistent UX.
 * Per research: Always normalize errors to a consistent AppError format.
 */

import type { AxiosError } from 'axios';

/**
 * Normalized application error structure
 */
export interface AppError {
  message: string;
  code: string;
  status?: number;
  details?: Record<string, unknown>;
}

/**
 * Type guard for Axios errors
 */
function isAxiosError(error: unknown): error is AxiosError {
  return (
    error !== null &&
    typeof error === 'object' &&
    'isAxiosError' in error &&
    (error as AxiosError).isAxiosError === true
  );
}

/**
 * Normalize any error to AppError format
 *
 * Handles:
 * - Axios errors (API responses)
 * - Standard Error objects
 * - String errors
 * - Unknown error types
 */
export function normalizeError(error: unknown): AppError {
  console.debug('[API] Normalizing error:', error);

  // Axios error with response
  if (isAxiosError(error)) {
    const axiosError = error as AxiosError<{ detail?: string; message?: string }>;
    const status = axiosError.response?.status;
    const data = axiosError.response?.data;

    return {
      message: data?.detail || data?.message || axiosError.message || 'API request failed',
      code: `HTTP_${status || 'UNKNOWN'}`,
      status,
      details: data as Record<string, unknown> | undefined,
    };
  }

  // Standard Error object
  if (error instanceof Error) {
    return {
      message: error.message,
      code: error.name || 'ERROR',
    };
  }

  // String error
  if (typeof error === 'string') {
    return {
      message: error,
      code: 'STRING_ERROR',
    };
  }

  // Unknown error
  return {
    message: 'An unexpected error occurred',
    code: 'UNKNOWN_ERROR',
    details: { rawError: String(error) },
  };
}

/**
 * Check if error indicates network/connection issue
 */
export function isNetworkError(error: AppError): boolean {
  return error.code === 'HTTP_UNKNOWN' || error.message.includes('Network Error');
}

/**
 * Check if error indicates unauthorized (401)
 */
export function isUnauthorizedError(error: AppError): boolean {
  return error.status === 401;
}

/**
 * Check if error indicates not found (404)
 */
export function isNotFoundError(error: AppError): boolean {
  return error.status === 404;
}
