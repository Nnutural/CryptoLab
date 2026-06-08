import client, { type APIResponse } from "./client";

export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface RegisterResponse {
  user_id: number;
  created_at: string;
}

export interface CurrentUser {
  user_id: number;
  username: string;
  role: string;
  created_at: string;
  last_login_at: string | null;
}

export async function login(username: string, password: string): Promise<APIResponse<LoginResponse>> {
  return client.post("/auth/login", { username, password });
}

export async function register(username: string, password: string): Promise<APIResponse<RegisterResponse>> {
  return client.post("/auth/register", { username, password });
}

export async function logout(): Promise<APIResponse<null>> {
  return client.post("/auth/logout");
}

export async function getMe(): Promise<APIResponse<CurrentUser>> {
  return client.get("/auth/me");
}
