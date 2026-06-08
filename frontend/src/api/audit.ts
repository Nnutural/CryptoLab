import client, { type APIResponse } from "./client";

export async function getAuditLogs(params?: Record<string, any>): Promise<APIResponse<any[]>> {
  return client.get("/audit/logs", { params });
}
