import axios, { type AxiosInstance } from 'axios'

const client: AxiosInstance = axios.create({
  baseURL: '/api/v1',
  timeout: 30_000
})

client.interceptors.request.use((config) => {
  const token = localStorage.getItem('cryptolab.jwt')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

client.interceptors.response.use(
  (resp) => resp.data,
  (err) => {
    // TODO: route 401 → /login, surface APIResponse.message via Element Plus notification
    return Promise.reject(err)
  }
)

export default client
