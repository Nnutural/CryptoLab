import client, { type APIResponse } from "./client";

type BackendKey = {
  id?: string;
  key_id?: string;
  key_type?: string;
  type?: string;
  algorithm?: string;
  paired_key_id?: string | null;
  pair_id?: string | null;
  label?: string | null;
  created_at?: string;
  expires_at?: string | null;
};

function normalizeKey(row: BackendKey): BackendKey {
  const keyId = row.key_id ?? row.id ?? "";
  return {
    ...row,
    id: row.id ?? keyId,
    key_id: keyId,
    type: row.type ?? row.key_type,
    pair_id: row.pair_id ?? row.paired_key_id ?? null,
  };
}

export async function listKeys(): Promise<APIResponse<any[]>> {
  const resp = await client.get("/keys") as APIResponse<BackendKey[]>;
  return {
    ...resp,
    data: Array.isArray(resp.data) ? resp.data.map(normalizeKey) : [],
  };
}

export async function getKeyPublic(keyId: string): Promise<APIResponse<any>> {
  return client.get(`/keys/${keyId}/public`);
}

export async function deleteKey(keyId: string): Promise<APIResponse<null>> {
  return client.delete(`/keys/${keyId}`);
}
