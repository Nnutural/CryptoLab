import client, { type APIResponse } from "./client";

export async function secureFileSend(body: any): Promise<APIResponse<any>> {
  return client.post("/scenarios/secure_file_transfer/send", body);
}

export async function secureFileReceive(body: any): Promise<APIResponse<any>> {
  return client.post("/scenarios/secure_file_transfer/receive", body);
}
