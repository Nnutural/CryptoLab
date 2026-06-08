import client, { type APIResponse } from "./client";

export async function rsaKeygen(body: { bits?: number; e?: number; label?: string }): Promise<APIResponse<any>> {
  return client.post("/pubkey/rsa/keygen", body);
}

export async function rsaEncrypt(body: { plaintext: string; key_id: string }): Promise<APIResponse<any>> {
  return client.post("/pubkey/rsa/encrypt", body);
}

export async function rsaDecrypt(body: { ciphertext_hex: string; key_id: string }): Promise<APIResponse<any>> {
  return client.post("/pubkey/rsa/decrypt", body);
}

export async function rsaSign(body: { message: string; key_id: string }): Promise<APIResponse<any>> {
  return client.post("/pubkey/rsa/sign", body);
}

export async function rsaVerify(body: { message: string; signature_hex: string; key_id: string }): Promise<APIResponse<any>> {
  return client.post("/pubkey/rsa/verify", body);
}

export async function eccKeygen(body: { curve?: string; label?: string }): Promise<APIResponse<any>> {
  return client.post("/pubkey/ecc/keygen", body);
}

export async function ecdsaSign(body: { message: string; key_id: string; curve?: string }): Promise<APIResponse<any>> {
  return client.post("/pubkey/ecdsa/sign", body);
}

export async function ecdsaVerify(body: { message: string; r_hex: string; s_hex: string; key_id: string; curve?: string }): Promise<APIResponse<any>> {
  return client.post("/pubkey/ecdsa/verify", body);
}
