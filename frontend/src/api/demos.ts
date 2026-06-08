import client, { type APIResponse } from "./client";

export async function ecbImageLeak(body: any): Promise<APIResponse<any>> {
  return client.post("/demos/ecb_image_leak", body);
}

export async function ecdsaKReuse(body: any): Promise<APIResponse<any>> {
  return client.post("/demos/ecdsa_k_reuse", body);
}

export async function rsaLowExponent(body: any): Promise<APIResponse<any>> {
  return client.post("/demos/rsa_low_exponent", body);
}

export async function pbkdf2Impact(body: any): Promise<APIResponse<any>> {
  return client.post("/demos/pbkdf2_iteration_impact", body);
}
