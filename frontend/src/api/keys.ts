import client, { type APIResponse } from "./client";

export async function listKeys(): Promise<APIResponse<any[]>> {
  return client.get("/keys");
}

export async function getKeyPublic(keyId: string): Promise<APIResponse<any>> {
  return client.get(`/keys/${keyId}/public`);
}

export async function deleteKey(keyId: string): Promise<APIResponse<null>> {
  return client.delete(`/keys/${keyId}`);
}
