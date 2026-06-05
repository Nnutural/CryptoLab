import client from './client'

export const hash = (algo: string, payload: unknown) =>
  client.post(`/hash/${algo}`, payload)

export const hmac = (algo: string, payload: unknown) =>
  client.post(`/hash/hmac/${algo}`, payload)

export const pbkdf2 = (payload: unknown) => client.post('/hash/pbkdf2', payload)
