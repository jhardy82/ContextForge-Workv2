/**
 * Feature-Specific QSE (Quantum Sync Engine) Hooks
 *
 * Implements manual API client for QSE endpoints since separate code generation
 * is not yet configured for this router.
 */

import { useQuery } from "@tanstack/react-query";
import { customInstance } from "../../lib/axios-instance";
import { normalizeError } from "../errors";

// --- Types (Matching Backend Scemas) ---

export interface GateResponse {
  id: string;
  name: string;
  description?: string | null;
  gate_type: string;
  threshold_value?: number | null;
  threshold_operator: string;
  severity: string;
  criteria?: Record<string, unknown> | null;
  enabled: boolean;
  created_at: string;
  created_by?: string | null;
}

export interface EvaluationResponse {
  id: string;
  gate_id: string;
  task_id?: string | null;
  actual_value: number;
  passed: boolean;
  evidence_ids: string[];
  evaluated_at: string;
  evaluated_by?: string | null;
}

export interface ListEvaluationsParams {
  task_id?: string;
  gate_id?: string;
  passed?: boolean;
  limit?: number;
}

// --- Fetch Functions ---

const listGates = async (enabledOnly: boolean = true) => {
  return customInstance<GateResponse[]>({
    url: "/api/v1/qse/gates",
    method: "GET",
    params: { enabled_only: enabledOnly },
  });
};

const listEvaluations = async (params?: ListEvaluationsParams) => {
  return customInstance<EvaluationResponse[]>({
    url: "/api/v1/qse/evaluations",
    method: "GET",
    params,
  });
};

// --- Hooks ---

export function useQSEGates(
  enabledOnly: boolean = true,
  options?: { enabled?: boolean }
) {
  const query = useQuery({
    queryKey: ["/api/v1/qse/gates", { enabledOnly }],
    queryFn: () => listGates(enabledOnly),
    enabled: options?.enabled ?? true,
  });

  return {
    gates: query.data ?? [],
    isLoading: query.isLoading,
    isError: query.isError,
    error: query.error ? normalizeError(query.error) : null,
    refetch: query.refetch,
  };
}

export function useQSEEvaluations(
  params?: ListEvaluationsParams,
  options?: { enabled?: boolean; refetchInterval?: number }
) {
  const query = useQuery({
    queryKey: ["/api/v1/qse/evaluations", params],
    queryFn: () => listEvaluations(params),
    enabled: options?.enabled ?? true,
    refetchInterval: options?.refetchInterval,
  });

  return {
    evaluations: query.data ?? [],
    isLoading: query.isLoading,
    isError: query.isError,
    error: query.error ? normalizeError(query.error) : null,
    refetch: query.refetch,
  };
}
