import client, { type APIResponse } from "./client";

export async function runBenchmark(algo: string): Promise<APIResponse<any>> {
  return client.get(`/benchmark/${algo}`);
}
