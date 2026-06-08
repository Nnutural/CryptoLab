import client, { type APIResponse } from "./client";

export async function base64Encode(data: string): Promise<APIResponse<any>> {
  return client.post("/encoding/base64/encode", { data });
}

export async function base64Decode(encoded: string): Promise<APIResponse<any>> {
  return client.post("/encoding/base64/decode", { encoded });
}
