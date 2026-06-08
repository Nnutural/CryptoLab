import client, { type APIResponse } from "./client";

export interface MetricPoint {
  algorithm: string;
  operation: string;
  duration_ns: number;
  recorded_at: string;
}

export interface MetricsParams {
  algorithm?: string;
  operation?: string;
  since?: string;
  until?: string;
  limit?: number;
}

function normalizeMetric(row: Partial<MetricPoint>): MetricPoint {
  return {
    algorithm: String(row.algorithm ?? "unknown"),
    operation: String(row.operation ?? "unknown"),
    duration_ns: Number(row.duration_ns ?? 0),
    recorded_at: String(row.recorded_at ?? new Date(0).toISOString()),
  };
}

export async function getMetrics(params?: MetricsParams): Promise<APIResponse<MetricPoint[]>> {
  const resp = (await client.get("/metrics", { params })) as APIResponse<MetricPoint[]>;
  return {
    ...resp,
    data: Array.isArray(resp.data) ? resp.data.map(normalizeMetric) : [],
  };
}
