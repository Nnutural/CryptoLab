import axios from "axios";

const client = axios.create({
  baseURL: "/api/v1",
  timeout: 30_000,
});

client.interceptors.request.use((config) => {
  const token = localStorage.getItem("cryptolab.jwt");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

client.interceptors.response.use(
  (resp) => resp.data,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem("cryptolab.jwt");
      window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);

export default client;

export interface APIResponse<T> {
  code: number;
  message: string;
  data: T;
  trace_id: string;
}
