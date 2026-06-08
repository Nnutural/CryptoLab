import client, { type APIResponse } from "./client";

type BackendAuditLog = {
  id?: number;
  log_id?: number | string;
  operation?: string;
  operation_type?: string;
  status_code?: number;
  status?: number;
  client_ip?: string | null;
  ip_address?: string | null;
  [key: string]: any;
};

function normalizeLog(row: BackendAuditLog): BackendAuditLog {
  return {
    ...row,
    log_id: row.log_id ?? row.id,
    operation_type: row.operation_type ?? row.operation,
    status: row.status ?? row.status_code,
    ip_address: row.ip_address ?? row.client_ip,
  };
}

export async function getAuditLogs(params?: Record<string, any>): Promise<APIResponse<any[]>> {
  const resp = await client.get("/audit/logs", { params }) as APIResponse<BackendAuditLog[]>;
  return {
    ...resp,
    data: Array.isArray(resp.data) ? resp.data.map(normalizeLog) : [],
  };
}
