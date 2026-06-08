import client, { type APIResponse } from "./client";

export interface AesRoundTrace {
  round_index: number;
  after_sub_bytes: string;
  after_shift_rows: string;
  after_mix_columns: string | null;
  after_add_round_key: string;
}

export interface AesTrace {
  key_size_bits: number;
  total_rounds: number;
  plaintext_hex: string;
  round_keys_hex: string[];
  initial_add_round_key: string;
  rounds: AesRoundTrace[];
  ciphertext_hex: string;
  timings_ns: {
    key_expansion_ns: number;
    per_round_ns: number[];
    total_ns: number;
  };
}

export async function symmetricKeygen(body: { algorithm: string; key_size: number; label?: string }): Promise<APIResponse<any>> {
  return client.post("/symmetric/keygen", body);
}

export async function symmetricEncrypt(algo: string, body: any): Promise<APIResponse<any>> {
  return client.post(`/symmetric/${algo}/encrypt`, body);
}

export async function symmetricDecrypt(algo: string, body: any): Promise<APIResponse<any>> {
  return client.post(`/symmetric/${algo}/decrypt`, body);
}
