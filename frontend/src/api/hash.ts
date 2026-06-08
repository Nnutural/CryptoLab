import client, { type APIResponse } from "./client";

export async function computeHash(algo: string, data: string): Promise<APIResponse<any>> {
  return client.post(`/hash/${algo}`, { data });
}

export async function computeHmac(algo: string, body: { key: string; message: string; algorithm: string }): Promise<APIResponse<any>> {
  return client.post(`/hash/hmac/${algo}`, body);
}

export async function computePbkdf2(body: { password: string; salt: string; iterations: number; key_len: number }): Promise<APIResponse<any>> {
  return client.post("/hash/pbkdf2", body);
}
