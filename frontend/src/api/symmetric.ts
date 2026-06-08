import client, { type APIResponse } from "./client";

export async function symmetricKeygen(body: { algorithm: string; key_size: number; label?: string }): Promise<APIResponse<any>> {
  return client.post("/symmetric/keygen", body);
}

export async function symmetricEncrypt(algo: string, body: any): Promise<APIResponse<any>> {
  return client.post(`/symmetric/${algo}/encrypt`, body);
}

export async function symmetricDecrypt(algo: string, body: any): Promise<APIResponse<any>> {
  return client.post(`/symmetric/${algo}/decrypt`, body);
}
